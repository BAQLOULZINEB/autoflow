"""Availability Agent — « Vérifier la disponibilité ».

Deterministic. No LLM call anywhere in this module: hallucinating a free
vehicle is structurally impossible. Every exclusion carries a reason so the
result is explainable to staff.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from pydantic import BaseModel, Field
from sqlalchemy import select

from ..db import Booking, Vehicle, session
from ..rules import load_rules


class Option(BaseModel):
    vehicle_id: str
    model: str
    category: str
    transmission: str
    location: str
    daily_rate_mad: int
    days: int
    total_mad: int
    pickup_date: str
    return_date: str
    note: str = ""


class AvailabilityResult(BaseModel):
    status: str = "unavailable"          # available | alternative | unavailable | invalid
    options: list[Option] = Field(default_factory=list)
    alternatives: list[Option] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    fleet_snapshot_at: str = ""
    computed_at: str = ""
    days: int = 0


def _d(s: str) -> date:
    return date.fromisoformat(s)


def _overlaps(a_start: date, a_end: date, b_start: date, b_end: date, buffer_h: int) -> bool:
    buf = timedelta(hours=buffer_h)
    a0, a1 = datetime.combine(a_start, datetime.min.time()), datetime.combine(a_end, datetime.min.time()) + buf
    b0, b1 = datetime.combine(b_start, datetime.min.time()), datetime.combine(b_end, datetime.min.time()) + buf
    return a0 < b1 and b0 < a1


def _check_vehicle(v: Vehicle, bookings: list[Booking], start: date, end: date, rules: dict) -> str | None:
    """Return None if free, else the reason it is not."""
    if v.status == "retired":
        return f"{v.id} : retiré de la flotte"
    if v.status == "maintenance":
        until = _d(v.maintenance_until) if v.maintenance_until else None
        if until is None or until >= start:
            return f"{v.id} : en maintenance" + (f" jusqu'au {until.strftime('%d/%m')}" if until else "")
    for b in bookings:
        if b.vehicle_id == v.id and b.status in ("confirmed", "pending") and \
                _overlaps(start, end, _d(b.start_date), _d(b.end_date), rules["buffer_hours"]):
            return f"{v.id} : réservé du {_d(b.start_date).strftime('%d/%m')} au {_d(b.end_date).strftime('%d/%m')}"
    return None


def _opt(v: Vehicle, start: date, end: date, note: str = "") -> Option:
    days = max(1, (end - start).days)
    return Option(vehicle_id=v.id, model=v.model, category=v.category, transmission=v.transmission,
                  location=v.location, daily_rate_mad=v.daily_rate_mad, days=days,
                  total_mad=days * v.daily_rate_mad, pickup_date=start.isoformat(),
                  return_date=end.isoformat(), note=note)


def check_availability(structured: dict, today: date) -> AvailabilityResult:
    rules = load_rules()
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    res = AvailabilityResult(computed_at=ts, fleet_snapshot_at=ts)
    p, r, cat = structured.get("pickup_date"), structured.get("return_date"), structured.get("vehicle_category")
    if not p or not r or not cat:
        res.status = "invalid"
        res.reasons.append("Demande incomplète : dates ou catégorie manquantes.")
        return res
    start, end = _d(p), _d(r)
    days = (end - start).days
    res.days = days
    if days < rules["min_days"]:
        res.status = "invalid"; res.reasons.append(f"Durée {days} j < minimum {rules['min_days']} j."); return res
    if days > rules["max_days"]:
        res.status = "invalid"; res.reasons.append(f"Durée {days} j > maximum {rules['max_days']} j."); return res
    if start < today:
        res.status = "invalid"; res.reasons.append("Date de prise en charge déjà passée."); return res

    want_tr = structured.get("transmission")
    want_loc = structured.get("pickup_location")

    with session() as db:
        vehicles = list(db.scalars(select(Vehicle)))
        bookings = list(db.scalars(select(Booking)))

    def rank(v: Vehicle) -> tuple:
        return (0 if want_loc and v.location == want_loc else 1,
                0 if want_tr and v.transmission == want_tr else 1, v.daily_rate_mad)

    # 1) exact category
    for v in sorted([v for v in vehicles if v.category == cat], key=rank):
        why = _check_vehicle(v, bookings, start, end, rules)
        if why:
            res.reasons.append(why); continue
        if want_tr and v.transmission != want_tr:
            res.reasons.append(f"{v.id} : libre mais boîte {v.transmission} (demandé : {want_tr})")
            res.alternatives.append(_opt(v, start, end, f"boîte {v.transmission}"))
            continue
        res.options.append(_opt(v, start, end))
    if res.options:
        res.status = "available"
        return res

    # 2) fallback categories, same dates
    for fb in rules["category_fallbacks"].get(cat, []):
        for v in sorted([v for v in vehicles if v.category == fb], key=rank):
            why = _check_vehicle(v, bookings, start, end, rules)
            if why:
                res.reasons.append(why); continue
            note = f"catégorie {fb} à la place de {cat}"
            if want_tr and v.transmission != want_tr:
                note += f", boîte {v.transmission}"
            res.alternatives.append(_opt(v, start, end, note))

    # 3) same category, shifted dates (± shift_days_allowed)
    shift = rules["shift_days_allowed"]
    for delta in range(1, shift + 1):
        for sign in (1, -1):
            s2, e2 = start + timedelta(days=sign * delta), end + timedelta(days=sign * delta)
            if s2 < today:
                continue
            for v in [v for v in vehicles if v.category == cat]:
                if _check_vehicle(v, bookings, s2, e2, rules) is None:
                    res.alternatives.append(_opt(v, s2, e2, f"dates décalées de {sign*delta:+d} j"))
        if len(res.alternatives) >= 4:
            break

    res.alternatives = res.alternatives[:4]
    res.status = "alternative" if res.alternatives else "unavailable"
    if res.status == "unavailable":
        res.reasons.append("Aucun véhicule ni alternative dans les règles configurées.")
    return res

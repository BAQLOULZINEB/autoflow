"""Excel workbook import — loads the agency's operational database.

Validates every row (reversed dates, duplicate MATRICULE in the same period,
CIN format, required fields) and logs each warning. Invalid rows are skipped
and counted. The import is always atomic (all or nothing within each sheet).

Sheets consumed: Locations, Flotte, Clients, Depenses, RendezVous
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from io import BytesIO
from typing import Any

from openpyxl import load_workbook
from sqlalchemy import text

from .db import (Base, Booking, Customer, Event, Request, Setting, Vehicle,
                 get_engine, init_db, session, utcnow)

# --------------------------------------------------------------------------- #
# Data models for the workbook rows (kept separate from the SQLAlchemy ORM)
# --------------------------------------------------------------------------- #
CIN_RE = re.compile(r"^[A-Z]{1,3}\d{5,7}$")
PASSPORT_RE = re.compile(r"^[A-Z]{2}\d{7}$")

VALID_CATS = {"citadine", "berline", "suv", "4x4", "utilitaire", "premium"}
VALID_STATUS = {"active", "maintenance", "retired"}
VALID_LOC_STATUS = {"terminee", "en_cours", "reservee", "Terminée", "En cours", "Réservée"}
LOC_STATUS_MAP = {"Terminée": "terminee", "En cours": "en_cours", "Réservée": "reservee",
                  "terminee": "terminee", "en_cours": "en_cours", "reservee": "reservee"}

EXPENSE_CATS = {"Leasing", "Assurance", "Vignette", "Vidange", "Pneus", "Réparation", "Lavage",
                "Visite technique", "Carburant", "Loyer", "Salaires", "Électricité & eau",
                "Internet & téléphone", "Marketing", "Comptabilité", "Logiciel"}


def _date(v: Any) -> date | None:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v).strip()[:10])
    except (ValueError, TypeError):
        return None


def _str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def _int(v: Any) -> int | None:
    if v is None:
        return None
    try:
        return int(float(str(v)))
    except (ValueError, TypeError):
        return None


# --------------------------------------------------------------------------- #
# Validation & import
# --------------------------------------------------------------------------- #
class ImportResult:
    def __init__(self):
        self.sheets: dict[str, dict] = {}
        self.warnings: list[str] = []
        self.errors: list[str] = []

    @property
    def ok(self) -> bool:
        return not self.errors

    def dict(self) -> dict:
        return {"ok": self.ok, "sheets": self.sheets, "warnings": self.warnings, "errors": self.errors}


def import_workbook(file_bytes: bytes) -> ImportResult:
    """Parse, validate, and import the workbook into the database."""
    result = ImportResult()
    try:
        wb = load_workbook(BytesIO(file_bytes), read_only=True, data_only=True)
    except Exception as exc:
        result.errors.append(f"Impossible d'ouvrir le fichier : {exc}")
        return result

    sheets = {s.lower(): s for s in wb.sheetnames}

    # — Flotte ---------------------------------------------------------------
    fleet_map: dict[str, dict] = {}  # plate → vehicle data
    if "flotte" in sheets:
        ws = wb[sheets["flotte"]]
        hdr = [_str(c).upper() for c in next(ws.iter_rows(max_row=1, values_only=True))]
        ok, skip = 0, 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            r = dict(zip(hdr, row))
            code = _str(r.get("CODE"))
            plate = _str(r.get("MATRICULE"))
            model = _str(r.get("MODELE"))
            cat = _str(r.get("CATEGORIE", "")).lower()
            tr = _str(r.get("BOITE", "manuelle"))
            loc = _str(r.get("AGENCE", "Agdal"))
            rate = _int(r.get("PRIX_JOUR"))
            status = _str(r.get("STATUT", "active")).lower()
            maint = _date(r.get("FIN_MAINTENANCE"))
            circ = _date(r.get("MISE_EN_CIRCULATION"))
            km = _int(r.get("KM"))
            ins = _date(r.get("ASSURANCE_EXPIRE"))
            vt = _date(r.get("VISITE_TECHNIQUE_EXPIRE"))

            warns = []
            if not plate:
                warns.append("MATRICULE vide"); skip += 1; result.warnings += warns; continue
            if cat and cat not in VALID_CATS:
                warns.append(f"Catégorie '{cat}' inconnue pour {plate}")
            if status not in VALID_STATUS:
                warns.append(f"Statut '{status}' non reconnu pour {plate}, corrigé en 'active'"); status = "active"
            if maint and status != "maintenance":
                warns.append(f"{plate} a une date de maintenance mais statut='{status}'")
            fleet_map[plate] = dict(code=code or plate, plate=plate, model=model, category=cat or "citadine",
                                    transmission=tr, location=loc, rate=rate or 250, status=status,
                                    maintenance_until=maint.isoformat() if maint else None,
                                    circ=circ, km=km or 0, insurance=ins, visite=vt)
            result.warnings += warns
            ok += 1
        result.sheets["Flotte"] = {"importés": ok, "ignorés": skip}
    else:
        result.warnings.append("Feuille 'Flotte' absente — les véhicules existants sont conservés.")

    # — Clients --------------------------------------------------------------
    clients_map: dict[str, dict] = {}  # CIN → client data
    if "clients" in sheets:
        ws = wb[sheets["clients"]]
        hdr = [_str(c).upper() for c in next(ws.iter_rows(max_row=1, values_only=True))]
        ok, skip = 0, 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            r = dict(zip(hdr, row))
            cin_val = _str(r.get("CIN"))
            name = _str(r.get("NOM"))
            phone = _str(r.get("TELEPHONE"))
            vip = _str(r.get("VIP", "non")).lower() in ("oui", "true", "1", "yes")
            notes = _str(r.get("NOTES"))
            code = _str(r.get("CODE")) or f"C-{len(clients_map) + 1:03d}"
            if not cin_val or not name:
                skip += 1; continue
            if not CIN_RE.match(cin_val) and not PASSPORT_RE.match(cin_val):
                result.warnings.append(f"CIN '{cin_val}' format inhabituel pour {name}")
            clients_map[cin_val] = dict(code=code, cin=cin_val, name=name, phone=phone, vip=vip, notes=notes)
            ok += 1
        result.sheets["Clients"] = {"importés": ok, "ignorés": skip}

    # — Locations (rentals) --------------------------------------------------
    rentals = []
    if "locations" in sheets:
        ws = wb[sheets["locations"]]
        hdr = [_str(c).upper() for c in next(ws.iter_rows(max_row=1, values_only=True))]
        ok, skip = 0, 0
        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            r = dict(zip(hdr, row))
            plate = _str(r.get("MATRICULE"))
            cin_val = _str(r.get("CIN"))
            prix = _int(r.get("PRIX_JOUR"))
            out = _date(r.get("DATE_SORTIE"))
            back = _date(r.get("DATE_ENTREE"))
            channel = _str(r.get("CANAL", "Comptoir"))
            status_raw = _str(r.get("STATUT", "terminee"))
            status = LOC_STATUS_MAP.get(status_raw, "terminee")
            loc_id = _str(r.get("N_LOCATION")) or f"L-{row_num:05d}"

            warns = []
            if not plate or not out:
                skip += 1; continue
            if back and out and back < out:
                warns.append(f"Ligne {row_num}: DATE_ENTREE < DATE_SORTIE pour {plate}, dates inversées")
                out, back = back, out
            if not back:
                back = out + timedelta(days=1)
                warns.append(f"Ligne {row_num}: DATE_ENTREE manquante pour {plate}, fixée à DATE_SORTIE + 1j")
            days = max(1, (back - out).days)
            if fleet_map and plate not in fleet_map:
                warns.append(f"Ligne {row_num}: MATRICULE '{plate}' absent de la Flotte")
            rentals.append(dict(id=loc_id, plate=plate, cin=cin_val, price=prix or 0, out=out, back=back,
                                days=days, amount=(prix or 0) * days, channel=channel, status=status))
            result.warnings += warns
            ok += 1
        result.sheets["Locations"] = {"importés": ok, "ignorés": skip}

        # duplicate-booking check
        by_plate: dict[str, list[dict]] = {}
        for rl in rentals:
            by_plate.setdefault(rl["plate"], []).append(rl)
        for plate, rents in by_plate.items():
            rents.sort(key=lambda x: x["out"])
            for i in range(len(rents) - 1):
                if rents[i]["back"] > rents[i + 1]["out"] and rents[i]["status"] != "terminee":
                    result.warnings.append(
                        f"Chevauchement détecté : {plate} du {rents[i]['out']} au {rents[i]['back']} "
                        f"et du {rents[i + 1]['out']} au {rents[i + 1]['back']}")

    # — Depenses -------------------------------------------------------------
    expenses = []
    if "depenses" in sheets:
        ws = wb[sheets["depenses"]]
        hdr = [_str(c).upper() for c in next(ws.iter_rows(max_row=1, values_only=True))]
        ok, skip = 0, 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            r = dict(zip(hdr, row))
            d = _date(r.get("DATE"))
            cat = _str(r.get("CATEGORIE"))
            amt = _int(r.get("MONTANT"))
            if not d or not amt:
                skip += 1; continue
            if cat and cat not in EXPENSE_CATS:
                result.warnings.append(f"Catégorie de dépense '{cat}' non standard")
            expenses.append(dict(date=d, plate=_str(r.get("MATRICULE")), category=cat, amount=amt,
                                 supplier=_str(r.get("FOURNISSEUR")), note=_str(r.get("NOTE"))))
            ok += 1
        result.sheets["Depenses"] = {"importés": ok, "ignorés": skip}

    # — RendezVous -----------------------------------------------------------
    appointments = []
    if "rendezvous" in sheets:
        ws = wb[sheets["rendezvous"]]
        hdr = [_str(c).upper() for c in next(ws.iter_rows(max_row=1, values_only=True))]
        ok, skip = 0, 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            r = dict(zip(hdr, row))
            d = _date(r.get("DATE"))
            if not d:
                skip += 1; continue
            appointments.append(dict(date=d, time=_str(r.get("HEURE", "09:00")), type=_str(r.get("TYPE")),
                                     plate=_str(r.get("MATRICULE")), cin=_str(r.get("CIN")),
                                     status=_str(r.get("STATUT", "prévu")), note=_str(r.get("NOTE"))))
            ok += 1
        result.sheets["RendezVous"] = {"importés": ok, "ignorés": skip}

    wb.close()

    if result.errors:
        return result

    # ---- Persist to database (atomic) -------------------------------------
    _persist(fleet_map, clients_map, rentals, expenses, appointments)
    return result


# --------------------------------------------------------------------------- #
def _persist(fleet_map, clients_map, rentals, expenses, appointments):
    """Write validated data to the SQLite database.

    For the V1 compatibility layer the data is mapped onto the existing
    Vehicle / Customer / Booking tables *and* into new analytics tables.
    """
    from .db import Base, get_engine
    from .analytics import AnalyticsBase, Expense, Appointment, Location
    eng = get_engine()
    AnalyticsBase.metadata.create_all(eng)

    with session() as db:
        # Vehicles
        if fleet_map:
            db.execute(text("DELETE FROM vehicles"))
            for v in fleet_map.values():
                db.add(Vehicle(id=v["code"], category=v["category"], model=v["model"],
                               transmission=v["transmission"], location=v["location"],
                               status=v["status"], maintenance_until=v["maintenance_until"],
                               daily_rate_mad=v["rate"]))
        # Customers
        if clients_map:
            db.execute(text("DELETE FROM customers"))
            for c in clients_map.values():
                db.add(Customer(id=c["code"], name=c["name"], phone_masked=c["phone"],
                                is_vip=c["vip"], notes=c["notes"]))
        # Bookings (from active/future rentals only — past ones go to Location analytics)
        today = date.today()
        db.execute(text("DELETE FROM bookings"))
        for r in rentals:
            if r["back"] >= today - timedelta(days=7):  # keep recent + future
                code = fleet_map.get(r["plate"], {}).get("code", r["plate"])
                db.add(Booking(id=r["id"], vehicle_id=code, start_date=r["out"].isoformat(),
                               end_date=r["back"].isoformat(), status="confirmed" if r["status"] != "terminee" else "confirmed"))
        # Locations (analytics table — all history)
        db.execute(text("DELETE FROM locations"))
        for r in rentals:
            db.add(Location(id=r["id"], plate=r["plate"], cin=r["cin"], price_per_day=r["price"],
                            date_out=r["out"], date_in=r["back"], days=r["days"], amount=r["amount"],
                            channel=r["channel"], status=r["status"]))
        # Expenses
        db.execute(text("DELETE FROM expenses"))
        for e in expenses:
            db.add(Expense(date=e["date"], plate=e["plate"] or None, category=e["category"],
                           amount=e["amount"], supplier=e["supplier"], note=e["note"]))
        # Appointments
        db.execute(text("DELETE FROM appointments"))
        for a in appointments:
            db.add(Appointment(date=a["date"], time=a["time"], type=a["type"], plate=a["plate"] or None,
                               cin=a["cin"] or None, status=a["status"], note=a["note"]))
        # metadata
        row = db.get(Setting, "excel_imported_at")
        ts = utcnow().isoformat()
        if row:
            row.value = ts
        else:
            db.add(Setting(key="excel_imported_at", value=ts))
        db.commit()

"""Service façade over the graph: submit, resume, follow-up sweep, KPIs, seed."""
from __future__ import annotations

import csv
import json
import uuid
from datetime import datetime, timedelta

from langgraph.types import Command
from sqlalchemy import func, select

from .. import clock
from ..config import DATA_DIR
from ..db import (Booking, Customer, Draft, Event, FollowUp, Request, Review, Setting, Vehicle, session,
                  utcnow)
from ..agents.followup import draft_reminder, recommend_when_stalled
from ..rules import load_rules
from . import store
from .graph import get_graph


def _cfg(request_id: str) -> dict:
    return {"configurable": {"thread_id": request_id}}


def new_request_id(db) -> str:
    n = db.scalar(select(func.count()).select_from(Request)) or 0
    return f"A-{n + 1:04d}"


# --------------------------------------------------------------------------- #
def submit(raw_message: str, channel: str = "whatsapp", customer_name: str = "", customer_id: str | None = None) -> str:
    now = clock.now()
    with session() as db:
        rid = new_request_id(db)
        if customer_id is None and customer_name:
            c = db.query(Customer).filter(Customer.name == customer_name).first()
            customer_id = c.id if c else None
        db.add(Request(id=rid, raw_message=raw_message.strip(), channel=channel, customer_name=customer_name,
                       customer_id=customer_id, received_at=now, state="new"))
        db.add(Event(request_id=rid, from_state=None, to_state="new", actor="system",
                     reason=f"Demande reçue via {channel}.", ts=now))
        db.commit()
    graph = get_graph()
    graph.invoke({"request_id": rid, "raw_message": raw_message, "channel": channel, "customer_name": customer_name,
                  "today": now.date().isoformat(), "hops": 0, "trace": []}, _cfg(rid))
    return rid


def pending_interrupt(request_id: str) -> dict | None:
    snap = get_graph().get_state(_cfg(request_id))
    for t in snap.tasks:
        if t.interrupts:
            return t.interrupts[0].value
    return None


def resume(request_id: str, decision: dict) -> dict:
    """Apply a staff/manager decision to the paused graph."""
    graph = get_graph()
    if pending_interrupt(request_id) is None:
        raise ValueError("Aucune validation en attente pour cette demande.")
    out = graph.invoke(Command(resume=decision), _cfg(request_id))
    return {"workflow_state": out.get("workflow_state")}


def customer_replied(request_id: str, accepted: bool, actor: str = "staff") -> None:
    """Pilot: staff records the customer's answer (no inbound connector)."""
    now = clock.now()
    store.cancel_followups(request_id, "customer_replied")
    if accepted:
        store.transition(request_id, "confirmed", actor, "Client a accepté ; réservation confirmée par l'équipe.", now=now, strict=False)
        with session() as db:
            req = db.get(Request, request_id)
            a = req.availability or {}
            best = (a.get("options") or a.get("alternatives") or [None])[0]
            if best:
                db.add(Booking(id=f"B-{uuid.uuid4().hex[:6].upper()}", vehicle_id=best["vehicle_id"], request_id=request_id,
                               start_date=best["pickup_date"], end_date=best["return_date"], status="confirmed"))
                db.commit()
    else:
        store.transition(request_id, "closed", actor, "Client a décliné.", now=now, strict=False)


# --------------------------------------------------------------------------- #
def sweep() -> dict:
    """Follow-up engine: mark due reminders, draft them, detect stalled leads.
    Runs on every dashboard load / clock advance — no background scheduler needed in the pilot."""
    now = clock.now()
    fu_rules = load_rules()["follow_up"]
    reminders, stalled = 0, 0
    with session() as db:
        due = db.query(FollowUp).filter(FollowUp.status == "scheduled", FollowUp.due_at <= now).all()
        ids = [(f.id, f.request_id, f.reminder_no) for f in due]
    for fid, rid, no in ids:
        with session() as db:
            req = db.get(Request, rid)
            if req.state != "pending_customer":
                f = db.get(FollowUp, fid); f.status = "cancelled"; f.outcome = f"state={req.state}"; db.commit(); continue
            f = db.get(FollowUp, fid); f.status = "due"; db.commit()
            structured, name = req.structured, req.customer_name
        out = draft_reminder(structured, no, name)
        store.add_draft(rid, "reminder", out.draft_fr, now=now)
        store.log(rid, "followup", f"Relance n°{no} due — brouillon préparé.", payload=out.model_dump(), now=now)
        store.save_fields(rid, followup=out.model_dump(), review_reason=f"Relance n°{no} à envoyer", review_level="staff")
        store.open_review(rid, f"Relance n°{no} à envoyer (aucune réponse client)", "staff", "normal", now=now)
        reminders += 1
    # stalled detection
    with session() as db:
        cand = db.query(Request).filter(Request.state == "pending_customer").all()
        items = [(r.id, r.customer_name, r.structured) for r in cand]
    for rid, name, structured in items:
        with session() as db:
            # the silence clock starts at the FIRST reply sent (reminders do not reset it);
            # a staff "client appelé" restarts it.
            first_sent = db.query(Draft).filter(Draft.request_id == rid, Draft.sent_at.isnot(None)).order_by(Draft.sent_at.asc()).first()
            sent_count = db.query(FollowUp).filter(FollowUp.request_id == rid, FollowUp.status == "done").count()
            ref = first_sent.sent_at if first_sent else None
            called = db.query(Event).filter(Event.request_id == rid, Event.to_state == "pending_customer",
                                            Event.reason.like("Client appelé%")).order_by(Event.ts.desc()).first()
            if called and ref and called.ts > ref:
                ref = called.ts
        if ref and now - ref >= timedelta(hours=fu_rules["stale_after_h"]):
            rec = recommend_when_stalled(sent_count)
            store.transition(rid, "stalled", "orchestrator", f"Aucune réponse depuis {fu_rules['stale_after_h']} h.", now=now)
            store.transition(rid, "needs_human", "orchestrator", rec.rationale, now=now)
            store.save_fields(rid, followup=rec.model_dump(), review_reason=rec.rationale, review_level="staff")
            store.open_review(rid, rec.rationale, "staff", "normal", now=now)
            store.cancel_followups(rid, "stalled")
            stalled += 1
    return {"reminders_due": reminders, "stalled": stalled, "now": now.isoformat(timespec="seconds")}


def send_reminder(request_id: str, actor: str, body: str | None = None) -> None:
    now = clock.now()
    fu_rules = load_rules()["follow_up"]
    with session() as db:
        f = db.query(FollowUp).filter(FollowUp.request_id == request_id, FollowUp.status == "due").order_by(FollowUp.id.desc()).first()
        if not f:
            raise ValueError("Aucune relance due.")
        f.status, f.outcome = "done", "sent"
        no = f.reminder_no
        last = db.query(Draft).filter_by(request_id=request_id, kind="reminder").order_by(Draft.id.desc()).first()
        if last:
            if body and body != last.body_fr:
                last.body_fr, last.edited = body, True
            last.sent_by, last.sent_at = actor, now
        db.commit()
    store.close_review(request_id, "approve", actor, "relance envoyée", now=now)
    store.transition(request_id, "pending_customer", actor, f"Relance n°{no} envoyée.", now=now)
    if no < fu_rules["max_reminders"]:
        store.schedule_followup(request_id, now + timedelta(hours=fu_rules["first_reminder_after_h"]), no + 1)


def staff_action_on_stalled(request_id: str, action: str, actor: str, note: str = "") -> None:
    now = clock.now()
    store.close_review(request_id, action, actor, note, now=now)
    if action == "close":
        store.transition(request_id, "closed", actor, f"Clôturé après relances. {note}".strip(), now=now, strict=False)
    elif action == "call_done":
        store.transition(request_id, "pending_customer", actor, f"Client appelé. {note}".strip(), now=now, strict=False)
        store.schedule_followup(request_id, now + timedelta(hours=load_rules()["follow_up"]["first_reminder_after_h"]), 1)


# --------------------------------------------------------------------------- #
def kpis() -> dict:
    """All KPIs derive from event timestamps. Demo numbers are counts, never % improvements."""
    with session() as db:
        reqs = db.query(Request).all()
        by_state = {s: 0 for s in ("new", "incomplete", "checked", "quote_ready", "pending_customer", "stalled",
                                    "needs_human", "escalated", "confirmed", "closed")}
        for r in reqs:
            by_state[r.state] = by_state.get(r.state, 0) + 1
        total = len(reqs)
        complete = sum(1 for r in reqs if r.structured and not r.structured.get("missing_fields"))
        # first draft time: received → first draft generated
        deltas = []
        for r in reqs:
            d = db.query(Draft).filter_by(request_id=r.id).order_by(Draft.id.asc()).first()
            if d:
                deltas.append((d.generated_at - r.received_at).total_seconds())
        reviews_open = db.query(Review).filter(Review.closed_at.is_(None)).count()
        reviews_manager = db.query(Review).filter(Review.closed_at.is_(None), Review.level == "manager").count()
        escalated_total = db.query(Event).filter(Event.to_state.in_(["needs_human", "escalated"]),
                                                 Event.from_state != Event.to_state).count()
        reminders_sent = db.query(FollowUp).filter(FollowUp.status == "done").count()
        reminders_due = db.query(FollowUp).filter(FollowUp.status == "due").count()
        events = db.query(Event).count()
    return {
        "total_requests": total,
        "by_state": by_state,
        "complete_rate": round(complete / total, 2) if total else None,
        "avg_seconds_to_first_draft": round(sum(deltas) / len(deltas), 1) if deltas else None,
        "reviews_open": reviews_open,
        "reviews_manager": reviews_manager,
        "human_handoffs": escalated_total,
        "reminders_sent": reminders_sent,
        "reminders_due": reminders_due,
        "events": events,
        "clock": clock.now().isoformat(timespec="seconds"),
        "label": "Données de démonstration — compteurs, pas de gains mesurés",
    }


# --------------------------------------------------------------------------- #
def reset_and_seed(with_history: bool = True) -> None:
    """Wipe everything and reload the mock fleet/bookings/customers."""
    from ..db import Base, get_engine
    eng = get_engine()
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    get_graph.cache_clear()
    try:
        import os
        from ..config import get_settings
        p = get_settings().checkpoint_db
        if os.path.exists(p):
            os.remove(p)
    except Exception:
        pass
    with session() as db:
        with open(DATA_DIR / "fleet.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                db.add(Vehicle(id=row["vehicle_id"], category=row["category"], model=row["model"],
                               transmission=row["transmission"], location=row["location"], status=row["status"],
                               maintenance_until=row["maintenance_until"] or None,
                               daily_rate_mad=int(row["daily_rate_mad"])))
        with open(DATA_DIR / "bookings.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                db.add(Booking(id=row["booking_id"], vehicle_id=row["vehicle_id"], start_date=row["start_date"],
                               end_date=row["end_date"], status=row["status"]))
        with open(DATA_DIR / "customers.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                db.add(Customer(id=row["customer_id"], name=row["name"], phone_masked=row["phone_masked"],
                                is_vip=row["is_vip"].lower() == "true", notes=row["notes"]))
        db.add(Setting(key="clock_offset_seconds", value="0"))
        db.add(Setting(key="seeded_at", value=utcnow().isoformat()))
        db.commit()
    if with_history:
        replay_history()


def replay_history(limit: int | None = None) -> dict:
    """Replay data/history.json as if the agency had used AutoFlow for 6 weeks.

    The demo clock is moved back to each message's timestamp, the request runs
    through the real graph, then the scripted human outcome is applied. Nothing
    is faked in the DB: every row comes from the normal code path.
    """
    from ..db import Draft
    p = DATA_DIR / "history.json"
    if not p.exists():
        return {"replayed": 0}
    items = json.loads(p.read_text(encoding="utf-8"))
    if limit:
        items = items[:limit]
    n = 0
    for h in items:
        clock.set_offset_hours(-h["days_ago"] * 24)
        rid = submit(h["message"], h["channel"], h["customer"])
        actor = "manager:Omar" if h["outcome"] in ("reject",) else "staff:Salma"
        with session() as db:
            req = db.get(Request, rid)
            level, state = req.review_level, req.state
        if level == "manager":
            actor = "manager:Omar"
        try:
            if pending_interrupt(rid) is None:
                continue
            oc = h["outcome"]
            if oc.startswith("complete"):
                resume(rid, {"action": "complete", "actor": actor, "fields": h["complete_fields"]})
                if pending_interrupt(rid) is not None:
                    resume(rid, {"action": "approve", "actor": actor, "note": "complété par téléphone"})
                oc = "approve_accept" if oc.endswith("accept") else "approve_pending"
            if oc.startswith("approve"):
                if state in ("escalated", "needs_human") and pending_interrupt(rid) is not None:
                    resume(rid, {"action": "approve", "actor": actor, "note": "validé"})
                elif pending_interrupt(rid) is not None:
                    resume(rid, {"action": "approve", "actor": actor})
                if oc.endswith("accept"):
                    clock.advance(rng_hours(6, 30))
                    customer_replied(rid, True, actor)
                elif oc.endswith("decline"):
                    clock.advance(rng_hours(6, 40))
                    customer_replied(rid, False, actor)
                elif oc.endswith("pending") and h["days_ago"] > 2:
                    # staff sends the first reminder when it becomes due; the lead then stalls naturally
                    clock.advance(26)
                    sweep()
                    try:
                        send_reminder(rid, "staff:Youssef")
                    except ValueError:
                        pass
            elif oc == "reject":
                resume(rid, {"action": "reject", "actor": actor, "note": "hors politique / non réalisable"})
            elif oc == "close":
                resume(rid, {"action": "close", "actor": actor, "note": "traité par téléphone" if state == "escalated" else "sans suite"})
        except Exception as exc:  # keep going: history is best-effort
            store.log(rid, "system", f"replay: {type(exc).__name__}: {exc}")
        n += 1
    clock.set_offset_hours(0)
    sweep()
    return {"replayed": n}


def rng_hours(a: float, b: float) -> float:
    import random
    return random.Random(a * 1000 + b).uniform(a, b)


def scenarios() -> list[dict]:
    return json.loads((DATA_DIR / "scenarios.json").read_text(encoding="utf-8"))

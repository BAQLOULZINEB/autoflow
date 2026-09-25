"""Persistence helpers used by graph nodes and the API.

`transition()` is the only way a request changes state: it validates the move
against TRANSITIONS and writes an Event. That is what makes the event log an
audit trail and KPIs computable.
"""
from __future__ import annotations

from datetime import datetime

from ..db import TRANSITIONS, Draft, Event, FollowUp, Request, Review, session, utcnow


class IllegalTransition(Exception):
    pass


def transition(request_id: str, to_state: str, actor: str, reason: str = "", payload: dict | None = None,
               now: datetime | None = None, strict: bool = True) -> str:
    with session() as db:
        req = db.get(Request, request_id)
        frm = req.state
        if frm != to_state and to_state not in TRANSITIONS.get(frm, set()):
            if strict:
                raise IllegalTransition(f"{frm} → {to_state}")
        req.state = to_state
        req.hops = (req.hops or 0) + 1
        db.add(Event(request_id=request_id, from_state=frm, to_state=to_state, actor=actor,
                     reason=reason, ts=now or utcnow(), payload=payload or {}))
        db.commit()
        return frm


def log(request_id: str, actor: str, reason: str, payload: dict | None = None, now: datetime | None = None) -> None:
    """Event without a state change (agent output, staff note...)."""
    with session() as db:
        req = db.get(Request, request_id)
        db.add(Event(request_id=request_id, from_state=req.state, to_state=req.state, actor=actor,
                     reason=reason, ts=now or utcnow(), payload=payload or {}))
        db.commit()


def save_fields(request_id: str, **fields) -> None:
    with session() as db:
        req = db.get(Request, request_id)
        for k, v in fields.items():
            setattr(req, k, v)
        db.commit()


def add_draft(request_id: str, kind: str, body: str, now: datetime | None = None) -> int:
    with session() as db:
        d = Draft(request_id=request_id, kind=kind, body_fr=body, generated_at=now or utcnow())
        db.add(d)
        db.commit()
        return d.id


def open_review(request_id: str, reason: str, level: str, priority: str, now: datetime | None = None) -> int:
    with session() as db:
        # one open review per request
        for r in db.query(Review).filter_by(request_id=request_id, closed_at=None):
            r.closed_at = now or utcnow(); r.decision = "superseded"
        rv = Review(request_id=request_id, reason=reason, level=level, priority=priority, opened_at=now or utcnow())
        db.add(rv)
        db.commit()
        return rv.id


def close_review(request_id: str, decision: str, actor: str, note: str = "", now: datetime | None = None) -> None:
    with session() as db:
        for r in db.query(Review).filter_by(request_id=request_id, closed_at=None):
            r.closed_at = now or utcnow(); r.decision = decision; r.actor = actor; r.note = note
        db.commit()


def schedule_followup(request_id: str, due_at: datetime, reminder_no: int) -> None:
    with session() as db:
        for f in db.query(FollowUp).filter_by(request_id=request_id, status="scheduled"):
            f.status = "cancelled"
        db.add(FollowUp(request_id=request_id, due_at=due_at, reminder_no=reminder_no))
        db.commit()


def cancel_followups(request_id: str, outcome: str) -> None:
    with session() as db:
        for f in db.query(FollowUp).filter_by(request_id=request_id).filter(FollowUp.status.in_(["scheduled", "due"])):
            f.status = "cancelled"; f.outcome = outcome
        db.commit()

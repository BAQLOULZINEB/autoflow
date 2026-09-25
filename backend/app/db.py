"""SQLAlchemy engine + declarative models.

Every table mirrors the pilot data model in docs (requests, vehicles, bookings,
drafts, follow_ups, reviews, events, rules). KPIs are never stored — they are
computed from `events` timestamps so they stay auditable.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# --------------------------------------------------------------------------- #
# Workflow states (docs/02-architecture §5). Plain strings so they read in the DB.
# --------------------------------------------------------------------------- #
STATES = ["new", "incomplete", "checked", "quote_ready", "pending_customer", "stalled",
          "needs_human", "escalated", "confirmed", "closed"]

TRANSITIONS: dict[str, set[str]] = {
    "new": {"incomplete", "checked", "needs_human", "escalated"},
    "incomplete": {"new", "needs_human", "checked", "closed"},
    "checked": {"quote_ready", "needs_human", "escalated"},
    "quote_ready": {"pending_customer", "needs_human", "closed"},
    "pending_customer": {"pending_customer", "confirmed", "stalled", "needs_human", "closed"},
    "stalled": {"needs_human", "pending_customer", "closed"},
    "needs_human": {"quote_ready", "escalated", "checked", "new", "closed"},
    "escalated": {"quote_ready", "confirmed", "closed", "needs_human"},
    "confirmed": {"closed"},
    "closed": set(),
}


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    phone_masked: Mapped[str] = mapped_column(String, default="")
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, default="")


class Vehicle(Base):
    __tablename__ = "vehicles"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    category: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    transmission: Mapped[str] = mapped_column(String, default="manuelle")
    location: Mapped[str] = mapped_column(String, default="Agdal")
    status: Mapped[str] = mapped_column(String, default="active")  # active | maintenance | retired
    maintenance_until: Mapped[str | None] = mapped_column(String, nullable=True)  # YYYY-MM-DD
    daily_rate_mad: Mapped[int] = mapped_column(Integer, default=300)


class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(ForeignKey("vehicles.id"))
    request_id: Mapped[str | None] = mapped_column(String, nullable=True)
    start_date: Mapped[str] = mapped_column(String)  # YYYY-MM-DD
    end_date: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="confirmed")


class Request(Base):
    __tablename__ = "requests"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    customer_name: Mapped[str] = mapped_column(String, default="")
    channel: Mapped[str] = mapped_column(String, default="whatsapp")
    raw_message: Mapped[str] = mapped_column(Text)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    state: Mapped[str] = mapped_column(String, default="new")
    intent: Mapped[str | None] = mapped_column(String, nullable=True)
    structured: Mapped[dict] = mapped_column(JSON, default=dict)     # StructuredRequest
    availability: Mapped[dict] = mapped_column(JSON, default=dict)   # AvailabilityResult
    followup: Mapped[dict] = mapped_column(JSON, default=dict)       # Follow-up agent output
    review_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    review_level: Mapped[str | None] = mapped_column(String, nullable=True)  # staff | manager
    priority: Mapped[str] = mapped_column(String, default="normal")  # normal | high
    assigned_to: Mapped[str | None] = mapped_column(String, nullable=True)
    hops: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class Draft(Base):
    __tablename__ = "drafts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("requests.id"))
    kind: Mapped[str] = mapped_column(String)  # quote | alternative | clarification | reminder
    body_fr: Mapped[str] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    edited: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_by: Mapped[str | None] = mapped_column(String, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class FollowUp(Base):
    __tablename__ = "follow_ups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("requests.id"))
    due_at: Mapped[datetime] = mapped_column(DateTime)
    reminder_no: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String, default="scheduled")  # scheduled | due | done | cancelled
    outcome: Mapped[str | None] = mapped_column(String, nullable=True)


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("requests.id"))
    reason: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String, default="staff")
    priority: Mapped[str] = mapped_column(String, default="normal")
    opened_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    decision: Mapped[str | None] = mapped_column(String, nullable=True)  # approve | edit | reject | close
    note: Mapped[str] = mapped_column(Text, default="")
    actor: Mapped[str | None] = mapped_column(String, nullable=True)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String, index=True)
    from_state: Mapped[str | None] = mapped_column(String, nullable=True)
    to_state: Mapped[str | None] = mapped_column(String, nullable=True)
    actor: Mapped[str] = mapped_column(String, default="system")  # system | intake | availability | followup | staff:<name>
    reason: Mapped[str] = mapped_column(Text, default="")
    ts: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)


class Setting(Base):
    __tablename__ = "settings"
    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(Text)


# --------------------------------------------------------------------------- #
_engine = None
_SessionLocal = None


def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        url = get_settings().database_url
        kw = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}
        _engine = create_engine(url, **kw)
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def session() -> Session:
    get_engine()
    return _SessionLocal()


def init_db() -> None:
    Base.metadata.create_all(get_engine())


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)

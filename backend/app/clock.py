"""Demo-controllable clock: now() = real UTC + an offset stored in `settings`.

The dashboard's "Avancer +24 h" button moves the offset; the follow-up sweep then
finds due reminders without waiting a day. Production leaves the offset at 0.
"""
from datetime import datetime, timedelta

from .db import Setting, session, utcnow


def _offset(db) -> int:
    row = db.get(Setting, "clock_offset_seconds")
    return int(row.value) if row else 0


def now() -> datetime:
    with session() as db:
        return utcnow() + timedelta(seconds=_offset(db))


def advance(hours: float) -> datetime:
    with session() as db:
        off = _offset(db) + int(hours * 3600)
        row = db.get(Setting, "clock_offset_seconds")
        if row:
            row.value = str(off)
        else:
            db.add(Setting(key="clock_offset_seconds", value=str(off)))
        db.commit()
    return now()


def set_offset_hours(hours: float) -> None:
    """Absolute offset (negative = travel to the past). Used by the history replay."""
    with session() as db:
        row = db.get(Setting, "clock_offset_seconds")
        val = str(int(hours * 3600))
        if row:
            row.value = val
        else:
            db.add(Setting(key="clock_offset_seconds", value=val))
        db.commit()


def reset() -> None:
    with session() as db:
        row = db.get(Setting, "clock_offset_seconds")
        if row:
            row.value = "0"
            db.commit()

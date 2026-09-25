"""Business rules — versioned JSON config, never hard-coded inside agents."""
import json
from functools import lru_cache

from .config import DATA_DIR

DEFAULT_RULES = {
    "version": 1,
    "min_days": 1,
    "max_days": 30,
    "max_auto_days": 14,
    "buffer_hours": 4,
    "shift_days_allowed": 3,
    "category_fallbacks": {
        "citadine": ["berline", "suv"],
        "berline": ["suv", "citadine"],
        "suv": ["berline", "4x4"],
        "4x4": ["suv"],
        "utilitaire": [],
    },
    "confidence_threshold": 0.75,
    "critical_field_threshold": 0.7,
    "high_value_threshold_mad": 6000,
    "follow_up": {"first_reminder_after_h": 24, "max_reminders": 2, "stale_after_h": 72},
    "auto_confirm": False,
    "agency": {"name": "Agence Mobilité Rabat", "locations": ["Agdal", "Hay Riad"],
               "deposit_mad": 3000, "km_per_day": 250},
}


@lru_cache
def load_rules() -> dict:
    p = DATA_DIR / "rules.json"
    if not p.exists():
        return DEFAULT_RULES
    data = json.loads(p.read_text(encoding="utf-8"))
    merged = {**DEFAULT_RULES, **data}
    merged["follow_up"] = {**DEFAULT_RULES["follow_up"], **data.get("follow_up", {})}
    merged["agency"] = {**DEFAULT_RULES["agency"], **data.get("agency", {})}
    return merged

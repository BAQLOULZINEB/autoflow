"""Intake Agent — « Comprendre la demande ».

Turns an unstructured customer message (French / light Darija) into a
StructuredRequest, or says precisely what is missing.

Two extraction engines, always both available:
  * rules   — regex + French date grammar; deterministic; runs offline.
  * llm     — optional (Anthropic / OpenAI / Ollama). Its output is only trusted
              when every field cites an `evidence` span found verbatim in the
              message. Fields without evidence are dropped. This is the
              structural anti-hallucination rule from the architecture doc.

The agent never decides anything. It reports intent, fields, confidence and
missing_fields; the orchestrator routes.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta

from pydantic import BaseModel, Field

from ..config import get_settings

CRITICAL_FIELDS = ("pickup_date", "return_date", "vehicle_category")

MONTHS = {
    "janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7,
    "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12,
    "jan": 1, "fev": 2, "avr": 4, "juil": 7, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}
CATEGORIES = {
    "citadine": ["citadine", "petite voiture", "clio", "i10", "sandero", "polo", "208"],
    "berline": ["berline", "308", "logan", "corolla", "accent"],
    "suv": ["suv", "duster", "tucson", "sportage", "crossover"],
    "4x4": ["4x4", "4 x 4", "pick-up", "pickup"],
    "utilitaire": ["utilitaire", "kangoo", "camionnette", "fourgon"],
}
LOCATIONS = {
    "Aeroport Rabat-Sale": ["aeroport", "aéroport", "airport", "rabat-sale", "rabat sale"],
    "Hay Riad": ["hay riad", "riad"],
    "Agdal": ["agdal", "rabat", "agence"],
    "Gare Rabat-Ville": ["gare"],
}
INTENT_KEYWORDS = {
    "complaint": ["probleme", "plainte", "reclamation", "panne", "personne ne repond", "mecontent",
                  "inadmissible", "remboursement", "pas normal", "deçu", "decu"],
    "modification": ["modifier", "changer", "decaler", "prolonger", "annuler", "reporter"],
    "reservation": ["reserver", "reservation", "confirmer", "bloquer"],
    "quote": ["louer", "location", "dispo", "disponible", "combien", "prix", "tarif", "devis", "voiture"],
    "info": ["caution", "kilometrage", "km", "conditions", "documents", "permis", "assurance"],
}
DISCOUNT_KEYWORDS = ["geste", "remise", "reduction", "réduction", "prix special", "moins cher", "negocier", "rabais"]
VIP_KEYWORDS = ["clients reguliers", "client regulier", "fidele", "habitue", "deja loue", "déjà loué"]
TRANSMISSION_KEYWORDS = {"automatique": ["automatique", "auto ", "boite auto", "bva"], "manuelle": ["manuelle", "boite manuelle"]}


class StructuredRequest(BaseModel):
    intent: str = "other"
    pickup_date: str | None = None      # YYYY-MM-DD
    return_date: str | None = None
    vehicle_category: str | None = None
    transmission: str | None = None
    pickup_location: str | None = None
    return_location: str | None = None
    budget_mad: int | None = None
    constraints: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)   # discount_requested, vip_claimed, ambiguous_dates
    field_confidence: dict[str, float] = Field(default_factory=dict)
    confidence: float = 0.0
    missing_fields: list[str] = Field(default_factory=list)
    clarification_fr: str | None = None
    evidence: dict[str, str] = Field(default_factory=dict)
    signals: dict[str, float] = Field(default_factory=dict)  # typed yes/no questions → probability (routing inputs)
    engine: str = "rules"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _next_occurrence(day: int, month: int, today: date) -> date:
    year = today.year
    try:
        d = date(year, month, day)
    except ValueError:
        return today
    if d < today - timedelta(days=30):
        d = date(year + 1, month, day)
    return d


def parse_dates(text: str, today: date) -> tuple[str | None, str | None, float, str]:
    """Return (pickup, return, confidence, evidence). Handles:
    'du 12 au 15 octobre', 'du 20/10 au 27/10', '12 au 15/10', 'le 12 octobre pour 3 jours',
    'ce week-end' / 'week-end prochain' (ambiguous → 0.55)."""
    t = _norm(text)
    mon = "|".join(MONTHS)
    # du 12 au 15 octobre  |  12 au 15 octobre
    m = re.search(rf"(\d{{1,2}})\s*({mon})?\s*(?:au|jusqu.au|-|→|a)\s*(\d{{1,2}})\s*({mon})", t)
    if m:
        d1, m1, d2, m2 = int(m.group(1)), m.group(2), int(m.group(3)), m.group(4)
        month2 = MONTHS[m2]
        month1 = MONTHS[m1] if m1 else month2          # "du 27 août au 17 septembre" vs "du 12 au 15 octobre"
        p, r = _next_occurrence(d1, month1, today), _next_occurrence(d2, month2, today)
        if r < p:
            r = _next_occurrence(d2, month2 + 1 if month2 < 12 else 1, today)
        return p.isoformat(), r.isoformat(), 0.92, m.group(0)
    # du 20/10 au 27/10 | 20/10 - 27/10
    m = re.search(r"(\d{1,2})[/.](\d{1,2})(?:[/.](\d{2,4}))?\s*(?:au|jusqu.au|-|a)\s*(\d{1,2})[/.](\d{1,2})", t)
    if m:
        p = _next_occurrence(int(m.group(1)), int(m.group(2)), today)
        r = _next_occurrence(int(m.group(4)), int(m.group(5)), today)
        return p.isoformat(), r.isoformat(), 0.9, m.group(0)
    # le 12 octobre pour 3 jours / 3 nuits
    m = re.search(rf"(\d{{1,2}})\s*({mon})\s*(?:pour|pendant)?\s*(\d{{1,2}})\s*(jours?|nuits?)", t)
    if m:
        p = _next_occurrence(int(m.group(1)), MONTHS[m.group(2)], today)
        return p.isoformat(), (p + timedelta(days=int(m.group(3)))).isoformat(), 0.85, m.group(0)
    # single explicit date only
    m = re.search(rf"(\d{{1,2}})\s*({mon})", t)
    if m:
        p = _next_occurrence(int(m.group(1)), MONTHS[m.group(2)], today)
        return p.isoformat(), None, 0.6, m.group(0)
    # relative / ambiguous
    if re.search(r"week.?end", t):
        # next Saturday → Sunday: a *guess*, flagged ambiguous
        days_ahead = (5 - today.weekday()) % 7 or 7
        if "prochain" in t:
            days_ahead += 7 if days_ahead < 3 else 0
        sat = today + timedelta(days=days_ahead)
        return sat.isoformat(), (sat + timedelta(days=1)).isoformat(), 0.55, re.search(r"[^.]*week.?end[^.?!]*", t).group(0)
    if "demain" in t:
        p = today + timedelta(days=1)
        return p.isoformat(), None, 0.5, "demain"
    return None, None, 0.0, ""


def _find(text_norm: str, table: dict[str, list[str]]) -> tuple[str | None, str]:
    for key, kws in table.items():
        for kw in kws:
            if _norm(kw) in text_norm:
                return key, kw
    return None, ""


def _intent(t: str, has_dates: bool = True) -> tuple[str, float]:
    # a question about deposit / km / documents without any date is an information request,
    # even if the customer mentions booking "later"
    if not has_dates and any(_norm(k) in t for k in INTENT_KEYWORDS["info"]) and             not any(_norm(k) in t for k in INTENT_KEYWORDS["complaint"]):
        return "info", 0.85
    for intent in ("complaint", "modification", "reservation", "quote", "info"):
        for kw in INTENT_KEYWORDS[intent]:
            if _norm(kw) in t:
                return intent, 0.9 if intent in ("complaint", "quote", "reservation") else 0.8
    return "other", 0.4


# --------------------------------------------------------------------------- #
# rules engine
# --------------------------------------------------------------------------- #
def extract_rules(message: str, today: date) -> StructuredRequest:
    t = _norm(message)
    req = StructuredRequest(engine="rules")
    p, r, dc, ev = parse_dates(message, today)
    req.intent, ic = _intent(t, has_dates=p is not None)
    req.field_confidence["intent"] = ic

    req.pickup_date, req.return_date = p, r
    req.field_confidence["pickup_date"] = dc if p else 0.0
    req.field_confidence["return_date"] = dc if r else 0.0
    if ev:
        req.evidence["dates"] = ev
    if p and dc < 0.7:
        req.flags.append("ambiguous_dates")

    cat, ev = _find(t, CATEGORIES)
    req.vehicle_category = cat
    req.field_confidence["vehicle_category"] = 0.9 if cat else 0.0
    if cat:
        req.evidence["vehicle_category"] = ev

    tr, ev = _find(t, TRANSMISSION_KEYWORDS)
    if tr:
        req.transmission, req.evidence["transmission"] = tr, ev.strip()

    # locations: "retour aéroport" → return; first mention otherwise → pickup
    m = re.search(r"retour\s+(?:a|à|au|a l.)?\s*([a-z' -]{3,25})", t)
    if m:
        loc, _ = _find(m.group(1), LOCATIONS)
        if loc:
            req.return_location, req.evidence["return_location"] = loc, m.group(0).strip()
    loc, ev = _find(t.replace(m.group(0), "") if m else t, LOCATIONS)
    if loc:
        req.pickup_location, req.evidence["pickup_location"] = loc, ev
    if req.return_location is None and req.pickup_location:
        req.return_location = req.pickup_location

    m = re.search(r"(\d{3,5})\s*(?:dh|dhs|mad|dirhams?)", t)
    if m:
        req.budget_mad, req.evidence["budget"] = int(m.group(1)), m.group(0)

    for kw in DISCOUNT_KEYWORDS:
        if _norm(kw) in t:
            req.flags.append("discount_requested"); req.evidence["discount"] = kw; break
    for kw in VIP_KEYWORDS:
        if _norm(kw) in t:
            req.flags.append("vip_claimed"); req.evidence["vip"] = kw; break

    _finalise(req)
    return req


def _finalise(req: StructuredRequest) -> None:
    """Compute missing fields, overall confidence and a French clarification."""
    # a message with dates + category is a quote request even without a keyword
    if req.intent == "other" and req.vehicle_category and req.pickup_date:
        req.intent, req.field_confidence["intent"] = "quote", 0.8
    if req.intent in ("quote", "reservation", "modification", "other"):
        req.missing_fields = [f for f in CRITICAL_FIELDS if getattr(req, f) is None]
        if req.pickup_location is None:
            # not critical: default to the main agency location, flagged for staff
            req.pickup_location = "Agdal"
            req.field_confidence["pickup_location"] = 0.5
            req.flags.append("location_defaulted")
            if req.return_location is None:
                req.return_location = req.pickup_location
    crit = [req.field_confidence.get(f, 0.0) for f in CRITICAL_FIELDS]
    base = (req.field_confidence.get("intent", 0.5) + sum(crit)) / 4
    req.confidence = round(min(1.0, base + (0.05 if "location_defaulted" not in req.flags else 0)), 2)
    if req.intent == "complaint":
        req.confidence = max(req.confidence, req.field_confidence.get("intent", 0.9))
        req.missing_fields = []

    # Routing questions answered as calibrated probabilities, not prose
    # (the orchestrator only ever reads these + thresholds from rules.json).
    ic = req.field_confidence.get("intent", 0.5)
    req.signals = {
        "is_complaint": round(ic if req.intent == "complaint" else 1 - ic, 2),
        "wants_quote_or_booking": round(ic if req.intent in ("quote", "reservation") else 1 - ic, 2),
        "discount_requested": 0.95 if "discount_requested" in req.flags else 0.05,
        "vip_claimed": 0.9 if "vip_claimed" in req.flags else 0.1,
        "dates_ambiguous": round(1 - req.field_confidence.get("pickup_date", 0.0), 2),
        "request_complete": round(0.0 if req.missing_fields else req.confidence, 2),
    }

    asks = []
    if "pickup_date" in req.missing_fields or "return_date" in req.missing_fields or "ambiguous_dates" in req.flags:
        asks.append("les dates exactes de prise et de retour")
    if "vehicle_category" in req.missing_fields:
        asks.append("la catégorie de véhicule souhaitée (citadine, berline, SUV…)")
    if "location_defaulted" in req.flags and asks:
        asks.append("le lieu de prise en charge (Agdal, Hay Riad, aéroport)")
    if asks:
        req.clarification_fr = ("Bonjour et merci pour votre message ! Pour vous répondre précisément, "
                                "pourriez-vous nous indiquer " + " et ".join(asks) + " ? Merci !")


# --------------------------------------------------------------------------- #
# optional LLM engine (evidence-gated)
# --------------------------------------------------------------------------- #
class _LLMExtraction(BaseModel):
    """Schema the LLM must fill. Every value needs a verbatim evidence span."""
    intent: str = Field(description="one of: info, quote, reservation, modification, complaint, other")
    pickup_date: str | None = Field(None, description="YYYY-MM-DD or null")
    return_date: str | None = Field(None, description="YYYY-MM-DD or null")
    vehicle_category: str | None = Field(None, description="citadine|berline|suv|4x4|utilitaire or null")
    transmission: str | None = None
    pickup_location: str | None = None
    return_location: str | None = None
    budget_mad: int | None = None
    discount_requested: bool = False
    vip_claimed: bool = False
    ambiguous_dates: bool = False
    evidence: dict[str, str] = Field(default_factory=dict,
                                     description="field name -> exact substring of the message that justifies it")


def _build_llm():
    s = get_settings()
    provider = s.llm_provider.lower()
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=s.llm_model, api_key=s.anthropic_api_key, temperature=0)
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=s.llm_model, api_key=s.openai_api_key, temperature=0)
    if provider == "ollama":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=s.llm_model, base_url=s.ollama_base_url, api_key="ollama", temperature=0)
    return None


def extract_llm(message: str, today: date) -> StructuredRequest | None:
    llm = _build_llm()
    if llm is None:
        return None
    prompt = (
        f"Tu es l'agent d'entrée d'une agence de location de voitures à Rabat. Date du jour : {today.isoformat()}.\n"
        "Extrais les champs du message client (français / darija). Pour CHAQUE champ rempli, mets dans `evidence` "
        "le passage EXACT du message qui le justifie. Si tu n'as pas de passage, laisse le champ null. "
        "N'invente rien.\n\nMessage :\n" + message
    )
    out: _LLMExtraction = llm.with_structured_output(_LLMExtraction).invoke(prompt)
    req = StructuredRequest(engine="llm", intent=out.intent)
    tn = _norm(message)
    for f in ("pickup_date", "return_date", "vehicle_category", "transmission", "pickup_location",
              "return_location", "budget_mad"):
        val = getattr(out, f)
        ev = out.evidence.get(f) or out.evidence.get("dates" if "date" in f else f, "")
        if val is not None and ev and _norm(ev) in tn:
            setattr(req, f, val)
            req.evidence[f] = ev
            req.field_confidence[f] = 0.88
        else:
            req.field_confidence[f] = 0.0
    req.field_confidence["intent"] = 0.85
    if out.discount_requested:
        req.flags.append("discount_requested")
    if out.vip_claimed:
        req.flags.append("vip_claimed")
    if out.ambiguous_dates:
        req.flags.append("ambiguous_dates")
        for f in ("pickup_date", "return_date"):
            req.field_confidence[f] = min(req.field_confidence.get(f, 0), 0.55)
    _finalise(req)
    return req


def run_intake(message: str, today: date, use_llm: bool | None = None) -> StructuredRequest:
    """Entry point used by the graph. LLM first (if enabled), rules as fallback / cross-check."""
    rules = extract_rules(message, today)
    if use_llm is None:
        use_llm = get_settings().llm_enabled
    if not use_llm:
        return rules
    try:
        llm = extract_llm(message, today)
    except Exception as exc:  # network / provider failure → rules-only, lower confidence
        rules.flags.append(f"llm_failed:{type(exc).__name__}")
        rules.confidence = round(rules.confidence * 0.9, 2)
        return rules
    if llm is None:
        return rules
    # Merge: keep LLM values, fill gaps from rules, agree → boost confidence
    for f in ("pickup_date", "return_date", "vehicle_category", "transmission", "pickup_location",
              "return_location", "budget_mad"):
        if getattr(llm, f) is None and getattr(rules, f) is not None:
            setattr(llm, f, getattr(rules, f))
            llm.field_confidence[f] = rules.field_confidence.get(f, 0.6)
            if f in rules.evidence:
                llm.evidence[f] = rules.evidence[f]
        elif getattr(llm, f) == getattr(rules, f) and getattr(llm, f) is not None:
            llm.field_confidence[f] = 0.95
    for fl in rules.flags:
        if fl not in llm.flags:
            llm.flags.append(fl)
    llm.engine = "llm+rules"
    _finalise(llm)
    return llm

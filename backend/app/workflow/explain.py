"""Decision trace — reconstruct *why* the orchestrator took each branch.

Read-only. Derives everything from persisted data (structured signals,
availability, review, events) plus the thresholds in rules.json, so the
explanation shown to the admin is exactly the rule set the graph executed.
"""
from __future__ import annotations

from ..db import Event, Request, session
from ..rules import load_rules
from .graph import MAX_HOPS

FR = {
    "intake": "Agent Intake — comprendre",
    "route_after_intake": "Orchestrateur — premier routage",
    "escalate": "Escalade manager",
    "clarify": "Question de clarification",
    "availability": "Agent Disponibilité — vérifier",
    "decide_after_availability": "Orchestrateur — matrice d'escalade",
    "sensitive": "Cas sensible → humain",
    "draft": "Agent Suivi — brouillon",
    "human_review": "Validation humaine (interrupt)",
    "finalize": "Finalisation",
    "sweep": "Moteur de relances",
}


def _check(rule: str, value, threshold, passed: bool, effect: str) -> dict:
    return {"rule": rule, "value": value, "threshold": threshold, "passed": passed, "effect": effect}


def explain(request_id: str, pending: dict | None) -> dict:
    rules = load_rules()
    with session() as db:
        r = db.get(Request, request_id)
        if not r:
            return {}
        events = [(e.actor, e.from_state, e.to_state, e.reason, e.ts.isoformat(timespec="seconds"))
                  for e in db.query(Event).filter_by(request_id=request_id).order_by(Event.id)]
        s, a, fu = r.structured or {}, r.availability or {}, r.followup or {}
        state, level = r.state, r.review_level
        hops = r.hops

    path: list[str] = []
    steps: list[dict] = []
    if not s:
        return {"path": ["intake"], "steps": [], "state": state}

    # ---- intake -----------------------------------------------------------
    path.append("intake")
    fc = s.get("field_confidence", {})
    steps.append({
        "node": "intake", "title": FR["intake"], "verdict": f"intent = {s.get('intent')} · confiance {s.get('confidence')}",
        "checks": [
            _check("moteur", s.get("engine"), "rules | llm+rules", True, "LLM seulement si preuve textuelle"),
            *[_check(f"preuve : {k}", v, "passage du message", True, "champ conservé") for k, v in (s.get("evidence") or {}).items()],
            *[_check(f"signal : {k}", v, "probabilité", True, "") for k, v in (s.get("signals") or {}).items()],
        ],
    })

    # ---- route_after_intake ---------------------------------------------
    crit_low = [f for f in ("pickup_date", "return_date", "vehicle_category") if fc.get(f, 0) < rules["critical_field_threshold"]]
    r1 = [
        _check("intent == complaint", s.get("intent"), "complaint", s.get("intent") == "complaint", "→ escalate"),
        _check("champs manquants", s.get("missing_fields") or [], "aucun", bool(s.get("missing_fields")), "→ clarify"),
        _check("confiance champ critique", {f: fc.get(f, 0) for f in ("pickup_date", "return_date", "vehicle_category")},
               f"≥ {rules['critical_field_threshold']}", bool(crit_low), "→ clarify"),
        _check("confiance globale", s.get("confidence"), f"≥ {rules['confidence_threshold']}",
               (s.get("confidence") or 0) < rules["confidence_threshold"], "→ clarify"),
    ]
    if s.get("intent") == "complaint":
        branch = "escalate"
    elif s.get("missing_fields") or crit_low or (s.get("confidence") or 0) < rules["confidence_threshold"]:
        branch = "clarify"
    else:
        branch = "availability"
    path.append("route_after_intake")
    steps.append({"node": "route_after_intake", "title": FR["route_after_intake"], "verdict": f"branche : {branch}", "checks": r1})
    path.append(branch)

    if branch == "escalate":
        steps.append({"node": "escalate", "title": FR["escalate"], "verdict": "manager · priorité haute · aucun brouillon",
                      "checks": [_check("règle", "réclamation", "toujours humain", True, "escalated")]})
    elif branch == "clarify":
        steps.append({"node": "clarify", "title": FR["clarify"], "verdict": f"brouillon de question · niveau {level or 'staff'}",
                      "checks": [_check("remise demandée", "discount_requested" in (s.get("flags") or []), "→ manager",
                                        "discount_requested" in (s.get("flags") or []), "niveau manager")]})
    if a.get("status"):
        if "availability" not in path:
            path.append("availability")  # re-run after "complete"
        steps.append({"node": "availability", "title": FR["availability"],
                      "verdict": f"{a['status']} · {len(a.get('options', []))} option(s) · {len(a.get('alternatives', []))} alternative(s) · {a.get('days')} j",
                      "checks": [_check("durée", a.get("days"), f"{rules['min_days']}–{rules['max_days']} j", True, ""),
                                 _check("tampon entre locations", f"{rules['buffer_hours']} h", "règle", True, ""),
                                 *[_check("exclusion", x, "", False, "") for x in (a.get("reasons") or [])[:6]]]})
        flags = s.get("flags") or []
        best = (a.get("options") or a.get("alternatives") or [{}])[0]
        r2 = [
            _check("hops", hops, f"≤ {MAX_HOPS}", hops > MAX_HOPS, "→ sensible"),
            _check("statut invalide / indisponible", a["status"], "available | alternative", a["status"] in ("invalid", "unavailable"), "→ sensible"),
            _check("remise demandée", "discount_requested" in flags, "non", "discount_requested" in flags, "→ manager"),
            _check("client régulier & alternative", ("vip_claimed" in flags) and a["status"] == "alternative", "non",
                   ("vip_claimed" in flags) and a["status"] == "alternative", "→ sensible"),
            _check("durée", a.get("days"), f"≤ {rules['max_auto_days']} j", (a.get("days") or 0) > rules["max_auto_days"], "→ manager"),
            _check("valeur", best.get("total_mad"), f"≤ {rules['high_value_threshold_mad']} MAD",
                   (best.get("total_mad") or 0) > rules["high_value_threshold_mad"], "→ manager"),
        ]
        sensitive = any(c["passed"] for c in r2)
        path.append("decide_after_availability")
        steps.append({"node": "decide_after_availability", "title": FR["decide_after_availability"],
                      "verdict": "cas sensible → humain" if sensitive else "cas standard → brouillon", "checks": r2})
        path.append("sensitive" if sensitive else "draft")
        steps.append({"node": "sensitive" if sensitive else "draft", "title": FR["sensitive" if sensitive else "draft"],
                      "verdict": f"{fu.get('draft_kind', 'none')} · action {fu.get('action', '-')}",
                      "checks": [_check("prix", "injecté depuis vehicles.daily_rate_mad", "jamais généré", True, "")]})

    # ---- human review / finalize ----------------------------------------
    path.append("human_review")
    human = [(act, frm, to, why, ts) for act, frm, to, why, ts in events if act.startswith(("staff", "manager"))]
    if pending:
        steps.append({"node": "human_review", "title": FR["human_review"], "verdict": f"en attente · {pending.get('review', {}).get('level')} · {pending.get('review', {}).get('reason', '')}",
                      "checks": [_check("actions possibles", pending.get("allowed"), "", True, "")], "waiting": True})
    else:
        steps.append({"node": "human_review", "title": FR["human_review"],
                      "verdict": "; ".join(f"{act} : {why}" for act, _, _, why, _ in human[-3:]) or "aucune décision encore",
                      "checks": [_check("décision", f"{act} → {to}", "", True, why) for act, _, to, why, _ in human]})
        if any(to in ("pending_customer", "closed", "confirmed") for _, _, to, _, _ in events):
            path.append("finalize")
            steps.append({"node": "finalize", "title": FR["finalize"], "verdict": f"état actuel : {state}",
                          "checks": [_check("relance planifiée", fu.get("next_check_at"), f"+{rules['follow_up']['first_reminder_after_h']} h", True, "")]})
    if any(act == "followup" and "Relance" in why for act, _, _, why, _ in events) or state in ("stalled",):
        path.append("sweep")
        steps.append({"node": "sweep", "title": FR["sweep"], "verdict": "relances / détection de lead sans réponse",
                      "checks": [_check("max relances", rules["follow_up"]["max_reminders"], "", True, ""),
                                 _check("sans réponse après", f"{rules['follow_up']['stale_after_h']} h", "", True, "→ stalled → humain")]})
    return {"path": path, "steps": steps, "state": state, "waiting": bool(pending)}

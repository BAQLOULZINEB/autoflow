"""The orchestrator as a LangGraph StateGraph.

    START → intake ─┬─ complaint ─────────────→ escalate ──→ human_review
                    ├─ incomplete / low conf → clarify ───→ human_review
                    └─ ok ─────────────────→ availability → decide ─→ draft → human_review
                                                                     └→ human_review (sensitive)
    human_review  = interrupt()  ← staff / manager decides in the dashboard
                  → finalize → END        (or Command(goto="availability") after "complete")

Design rules (from the architecture doc):
  * agents report, the orchestrator decides — routing only, never business commitments;
  * every state change goes through store.transition() → event log;
  * every human decision point is a real LangGraph interrupt, persisted by the
    checkpointer, so the process can stop, be restarted, and resume days later;
  * max hops → escalate (no infinite agent loops).
"""
from __future__ import annotations

from datetime import date, datetime
from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from ..agents.availability import check_availability
from ..agents.followup import draft_clarification, draft_quote, schedule_after_send
from ..agents.intake import run_intake
from ..config import get_settings
from ..rules import load_rules
from . import store
from .state import AutoFlowState

MAX_HOPS = 8


def _today(state: AutoFlowState) -> date:
    return date.fromisoformat(state["today"])


def _now(state: AutoFlowState) -> datetime:
    from .. import clock
    return clock.now()


# --------------------------------------------------------------------------- #
# Nodes
# --------------------------------------------------------------------------- #
def intake_node(state: AutoFlowState) -> dict:
    req = run_intake(state["raw_message"], _today(state))
    data = req.model_dump()
    store.save_fields(state["request_id"], structured=data, intent=req.intent)
    store.log(state["request_id"], "intake",
              f"Extraction ({req.engine}) : intent={req.intent}, confiance={req.confidence}, "
              f"manquants={req.missing_fields or 'aucun'}", payload=data, now=_now(state))
    return {"structured": data, "hops": state.get("hops", 0) + 1,
            "trace": [f"Intake : {req.intent} · confiance {req.confidence}"]}


def route_after_intake(state: AutoFlowState) -> str:
    s = state["structured"]
    rules = load_rules()
    if s["intent"] == "complaint":
        return "escalate"
    crit_low = any(s["field_confidence"].get(f, 0) < rules["critical_field_threshold"]
                   for f in ("pickup_date", "return_date", "vehicle_category"))
    if s["missing_fields"] or crit_low or s["confidence"] < rules["confidence_threshold"]:
        return "clarify"
    return "availability"


def escalate_node(state: AutoFlowState) -> dict:
    rid, now = state["request_id"], _now(state)
    reason = "Réclamation détectée : traitement prioritaire par le manager, aucun brouillon automatique."
    store.transition(rid, "escalated", "orchestrator", reason, now=now)
    store.save_fields(rid, review_reason=reason, review_level="manager", priority="high")
    store.open_review(rid, reason, "manager", "high", now=now)
    return {"workflow_state": "escalated", "review": {"level": "manager", "priority": "high", "reason": reason},
            "followup": {"draft_kind": "none", "draft_fr": "", "action": "escalate", "rationale": reason},
            "trace": ["Orchestrateur : escalade manager (réclamation)"]}


def clarify_node(state: AutoFlowState) -> dict:
    rid, now, s = state["request_id"], _now(state), state["structured"]
    fu = draft_clarification(s, state.get("customer_name", ""))
    store.add_draft(rid, "clarification", fu.draft_fr, now=now)
    reasons = []
    if s["missing_fields"]:
        reasons.append("champs manquants : " + ", ".join(s["missing_fields"]))
    if "ambiguous_dates" in s["flags"]:
        reasons.append("dates ambiguës")
    if s["confidence"] < load_rules()["confidence_threshold"]:
        reasons.append(f"confiance {s['confidence']} < seuil")
    level, prio = "staff", "normal"
    if "discount_requested" in s["flags"]:
        reasons.append("remise demandée → décision manager"); level, prio = "manager", "high"
    reason = "Demande incomplète — " + " ; ".join(reasons)
    store.transition(rid, "incomplete", "orchestrator", reason, now=now)
    store.transition(rid, "needs_human", "orchestrator", "Question de clarification préparée, validation humaine.", now=now)
    store.save_fields(rid, followup=fu.model_dump(), review_reason=reason, review_level=level, priority=prio)
    store.open_review(rid, reason, level, prio, now=now)
    return {"workflow_state": "needs_human", "followup": fu.model_dump(),
            "review": {"level": level, "priority": prio, "reason": reason},
            "trace": [f"Orchestrateur : {reason}"]}


def availability_node(state: AutoFlowState) -> dict:
    rid, now = state["request_id"], _now(state)
    res = check_availability(state["structured"], _today(state))
    data = res.model_dump()
    store.save_fields(rid, availability=data)
    store.log(rid, "availability", f"Disponibilité : {res.status} · {len(res.options)} option(s), "
              f"{len(res.alternatives)} alternative(s)", payload=data, now=now)
    store.transition(rid, "checked", "orchestrator", "Résultat de disponibilité validé (déterministe).", now=now)
    return {"availability": data, "workflow_state": "checked", "hops": state.get("hops", 0) + 1,
            "trace": [f"Disponibilité : {res.status}"]}


def decide_after_availability(state: AutoFlowState) -> str:
    """Escalation matrix (architecture doc §4)."""
    s, a, rules = state["structured"], state["availability"], load_rules()
    if state.get("hops", 0) > MAX_HOPS:
        return "sensitive"
    if a["status"] in ("invalid", "unavailable"):
        return "sensitive"
    if "discount_requested" in s["flags"]:
        return "sensitive"
    if a["status"] == "alternative" and "vip_claimed" in s["flags"]:
        return "sensitive"
    if a["days"] > rules["max_auto_days"]:
        return "sensitive"
    best = (a["options"] or a["alternatives"] or [{}])[0]
    if best.get("total_mad", 0) > rules["high_value_threshold_mad"]:
        return "sensitive"
    return "draft"


def _sensitive_reason(state: AutoFlowState) -> tuple[str, str, str]:
    s, a, rules = state["structured"], state["availability"], load_rules()
    reasons, level, prio = [], "staff", "normal"
    if state.get("hops", 0) > MAX_HOPS:
        reasons.append("nombre maximal d'étapes atteint")
    if a["status"] == "invalid":
        reasons.append("demande invalide : " + " ".join(a["reasons"][:1]))
    if a["status"] == "unavailable":
        reasons.append("aucun véhicule ni alternative")
    if "discount_requested" in s["flags"]:
        reasons.append("remise demandée"); level, prio = "manager", "high"
    if a["status"] == "alternative" and "vip_claimed" in s["flags"]:
        reasons.append("client régulier et véhicule demandé indisponible")
    if a["days"] > rules["max_auto_days"]:
        reasons.append(f"location longue ({a['days']} j > {rules['max_auto_days']} j)"); level = "manager"
    best = (a["options"] or a["alternatives"] or [{}])[0]
    if best.get("total_mad", 0) > rules["high_value_threshold_mad"]:
        reasons.append(f"valeur élevée ({best['total_mad']} MAD)"); level = "manager"
    return "Cas sensible — " + " ; ".join(reasons), level, prio


def sensitive_node(state: AutoFlowState) -> dict:
    rid, now = state["request_id"], _now(state)
    reason, level, prio = _sensitive_reason(state)
    # still prepare a draft when we have options, so staff starts from something
    fu = draft_quote(state["structured"], state["availability"], state.get("customer_name", ""))
    if fu.draft_fr:
        store.add_draft(rid, fu.draft_kind, fu.draft_fr, now=now)
    to_state = "escalated" if level == "manager" else "needs_human"
    store.transition(rid, to_state, "orchestrator", reason, now=now)
    store.save_fields(rid, followup=fu.model_dump(), review_reason=reason, review_level=level, priority=prio)
    store.open_review(rid, reason, level, prio, now=now)
    return {"workflow_state": to_state, "followup": fu.model_dump(),
            "review": {"level": level, "priority": prio, "reason": reason},
            "trace": [f"Orchestrateur : {reason}"]}


def draft_node(state: AutoFlowState) -> dict:
    rid, now = state["request_id"], _now(state)
    fu = draft_quote(state["structured"], state["availability"], state.get("customer_name", ""))
    store.add_draft(rid, fu.draft_kind, fu.draft_fr, now=now)
    store.log(rid, "followup", f"Brouillon {fu.draft_kind} préparé — {fu.rationale}", payload=fu.model_dump(), now=now)
    reason = "Devis standard prêt : l'équipe relit et envoie."
    store.transition(rid, "quote_ready", "orchestrator", reason, now=now)
    store.save_fields(rid, followup=fu.model_dump(), review_reason=reason, review_level="staff", priority="normal")
    store.open_review(rid, reason, "staff", "normal", now=now)
    return {"workflow_state": "quote_ready", "followup": fu.model_dump(),
            "review": {"level": "staff", "priority": "normal", "reason": reason},
            "trace": ["Follow-up : brouillon prêt"]}


def human_review_node(state: AutoFlowState) -> Command:
    """The human-in-the-loop gate. Execution pauses here until the dashboard resumes it."""
    decision = interrupt({
        "request_id": state["request_id"],
        "workflow_state": state.get("workflow_state"),
        "review": state.get("review", {}),
        "draft": state.get("followup", {}).get("draft_fr", ""),
        "allowed": ["approve", "edit", "reject", "close", "complete"],
    })
    if decision.get("action") == "complete":
        # staff filled missing fields → re-run availability with the completed request
        s = dict(state["structured"])
        s.update({k: v for k, v in decision.get("fields", {}).items() if v})
        for f in ("pickup_date", "return_date", "vehicle_category", "pickup_location"):
            if s.get(f):
                s["field_confidence"][f] = 1.0
        s["missing_fields"] = [f for f in ("pickup_date", "return_date", "vehicle_category") if not s.get(f)]
        s["flags"] = [f for f in s["flags"] if f != "ambiguous_dates"]
        s["confidence"] = 1.0 if not s["missing_fields"] else s["confidence"]
        rid, now = state["request_id"], _now(state)
        store.save_fields(rid, structured=s)
        store.close_review(rid, "complete", decision.get("actor", "staff"), decision.get("note", ""), now=now)
        store.transition(rid, "checked", decision.get("actor", "staff"),
                         "Champs complétés par l'équipe : nouvelle vérification de disponibilité.", now=now, strict=False)
        return Command(goto="availability", update={"structured": s, "decision": decision, "hops": state.get("hops", 0) + 1,
                                                    "trace": ["Équipe : champs complétés"]})
    return Command(goto="finalize", update={"decision": decision})


def finalize_node(state: AutoFlowState) -> dict:
    rid, now, d = state["request_id"], _now(state), state["decision"]
    actor = d.get("actor", "staff")
    action = d.get("action")
    note = d.get("note", "")
    cur = state.get("workflow_state")
    store.close_review(rid, action, actor, note, now=now)
    if action in ("approve", "edit"):
        body = d.get("body") or state.get("followup", {}).get("draft_fr", "")
        if action == "edit" and body:
            store.add_draft(rid, "edited", body, now=now)
        if cur in ("escalated", "needs_human"):
            store.transition(rid, "quote_ready", actor, f"Décision humaine : {action}. {note}".strip(), now=now)
        if body:
            # staff "sends" the reply (simulated in pilot) → waiting for the customer
            from ..db import Draft, session
            with session() as db:
                last = db.query(Draft).filter_by(request_id=rid).order_by(Draft.id.desc()).first()
                if last:
                    last.sent_by, last.sent_at, last.edited = actor, now, action == "edit"
                    db.commit()
            due = schedule_after_send(now)
            store.schedule_followup(rid, datetime.fromisoformat(due), 1)
            store.transition(rid, "pending_customer", actor, "Réponse envoyée par l'équipe ; relance planifiée.", now=now,
                             payload={"next_check_at": due})
            fu = dict(state.get("followup", {})); fu["next_check_at"] = due
            store.save_fields(rid, followup=fu)
            return {"workflow_state": "pending_customer", "followup": fu, "trace": [f"Équipe : {action} → envoyé"]}
        store.transition(rid, "closed", actor, f"Aucun message à envoyer. {note}".strip(), now=now, strict=False)
        return {"workflow_state": "closed", "trace": [f"Équipe : {action} → clos"]}
    if action == "reject":
        store.transition(rid, "closed", actor, f"Refusé par l'équipe. {note}".strip(), now=now, strict=False)
        store.cancel_followups(rid, "rejected")
        return {"workflow_state": "closed", "trace": ["Équipe : refusé"]}
    store.transition(rid, "closed", actor, f"Clôturé. {note}".strip(), now=now, strict=False)
    store.cancel_followups(rid, "closed")
    return {"workflow_state": "closed", "trace": ["Équipe : clos"]}


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_graph(checkpointer=None):
    g = StateGraph(AutoFlowState)
    g.add_node("intake", intake_node)
    g.add_node("escalate", escalate_node)
    g.add_node("clarify", clarify_node)
    g.add_node("availability", availability_node)
    g.add_node("sensitive", sensitive_node)
    g.add_node("draft", draft_node)
    g.add_node("human_review", human_review_node)
    g.add_node("finalize", finalize_node)

    g.add_edge(START, "intake")
    g.add_conditional_edges("intake", route_after_intake,
                            {"escalate": "escalate", "clarify": "clarify", "availability": "availability"})
    g.add_conditional_edges("availability", decide_after_availability, {"sensitive": "sensitive", "draft": "draft"})
    for n in ("escalate", "clarify", "sensitive", "draft"):
        g.add_edge(n, "human_review")
    g.add_edge("finalize", END)
    return g.compile(checkpointer=checkpointer or MemorySaver())


@lru_cache
def get_graph():
    """Process-wide compiled graph with a durable SQLite checkpointer.
    Falls back to memory (e.g. read-only serverless FS)."""
    try:
        import sqlite3
        from langgraph.checkpoint.sqlite import SqliteSaver
        conn = sqlite3.connect(get_settings().checkpoint_db, check_same_thread=False)
        return build_graph(SqliteSaver(conn))
    except Exception:
        return build_graph(MemorySaver())

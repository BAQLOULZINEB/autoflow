"""Built-in end-to-end simulations — scripted business cases that run through the
real API code path (submit → agents → human decision → customer reply → reminders)
and assert the expected outcome at every step.

They serve two purposes at once:
  * demo: the admin plays a case and watches the system + humans act, step by step;
  * test: every step carries an `expect` block, so the suite doubles as a living
    acceptance test (`tests/test_simulations.py` runs them all).

Nothing is faked: each step calls the same orchestrator functions as the buttons.
"""
from __future__ import annotations

import time
from datetime import datetime

from . import clock
from .db import Booking, Draft, FollowUp, Request, session
from .workflow import orchestrator as orch
from .workflow.store import IllegalTransition

# --------------------------------------------------------------------------- #
# Catalogue
# --------------------------------------------------------------------------- #
SIMULATIONS: list[dict] = [
    {
        "key": "standard-whatsapp",
        "title": "Devis standard — WhatsApp",
        "channel": "whatsapp", "customer": "Karim B.",
        "message": "Salam, je voudrais louer une citadine du 12 au 15 octobre, prise à l'agence de Rabat Agdal. C'est possible et c'est combien ?",
        "summary": "Le cas nominal : demande complète, véhicule disponible, devis relu et envoyé par l'équipe, client qui accepte.",
        "proves": ["Extraction avec preuves textuelles", "Disponibilité déterministe", "Une personne envoie", "Relance planifiée puis annulée à l'acceptation", "Réservation créée en base"],
        "steps": [
            {"do": "submit", "label": "Le client écrit sur WhatsApp", "who": "client",
             "expect": {"state": "quote_ready", "intent": "quote", "availability_status": "available", "options_include": "CIT-03", "last_draft_kind": "quote"}},
            {"do": "decide", "action": "approve", "actor": "staff:Salma", "label": "Salma relit le devis et l'envoie", "who": "staff",
             "expect": {"state": "pending_customer", "followups_scheduled": 1}},
            {"do": "customer", "accepted": True, "label": "Le client accepte → Salma confirme", "who": "client",
             "expect": {"state": "confirmed", "booking_created": True, "followups_scheduled": 0}},
        ],
    },
    {
        "key": "alternative-facebook",
        "title": "SUV indisponible → alternative — Facebook",
        "channel": "facebook", "customer": "Sara M.",
        "message": "Bonjour, un SUV automatique du 20 au 27 octobre, retour aéroport Rabat-Salé svp.",
        "summary": "Le véhicule demandé est en maintenance ou réservé : le système propose une berline automatique ou un décalage de dates, avec les raisons.",
        "proves": ["Raisons d'exclusion explicites", "Catégories de repli et dates décalées", "L'équipe modifie le brouillon avant envoi", "Relance à +24 h puis client qui décline"],
        "steps": [
            {"do": "submit", "label": "Message reçu via la page Facebook", "who": "client",
             "expect": {"state": "quote_ready", "availability_status": "alternative", "alternatives_include": "BER-02", "reasons_mention": "maintenance"}},
            {"do": "decide", "action": "edit", "actor": "staff:Youssef", "body_suffix": "\n\nPS : livraison à l'aéroport offerte pour cette alternative.",
             "label": "Youssef ajoute une phrase et envoie", "who": "staff",
             "expect": {"state": "pending_customer", "last_draft_edited": True}},
            {"do": "advance", "hours": 25, "label": "24 h plus tard, aucune réponse", "who": "system",
             "expect": {"state": "pending_customer", "last_draft_kind": "reminder", "review_open": True}},
            {"do": "send_reminder", "actor": "staff:Youssef", "label": "Youssef envoie la relance n°1", "who": "staff",
             "expect": {"state": "pending_customer", "reminders_sent": 1}},
            {"do": "customer", "accepted": False, "label": "Le client a trouvé ailleurs", "who": "client",
             "expect": {"state": "closed"}},
        ],
    },
    {
        "key": "ambiguous-instagram",
        "title": "Dates floues + remise demandée — Instagram",
        "channel": "instagram", "customer": "Famille Alaoui",
        "message": "Slt, dispo une voiture pour le week-end prochain ? On est des clients réguliers, un petit geste sur le prix serait apprécié 🙏",
        "summary": "Le cas sensible : dates ambiguës, pas de catégorie, remise demandée par un client régulier. Le manager complète, le système revérifie, le manager décide.",
        "proves": ["Confiance par champ < seuil → humain", "Remise → niveau manager", "Command(goto=availability) après complétion", "Matrice d'escalade rejouée", "Note de décision tracée"],
        "steps": [
            {"do": "submit", "label": "DM Instagram reçu", "who": "client",
             "expect": {"state": "needs_human", "review_level": "manager", "flags_include": ["ambiguous_dates", "discount_requested", "vip_claimed"], "last_draft_kind": "clarification"}},
            {"do": "decide", "action": "complete", "actor": "manager:Omar", "fields": {"pickup_date": "2026-10-24", "return_date": "2026-10-26", "vehicle_category": "citadine", "pickup_location": "Agdal"},
             "label": "Omar appelle le client, complète les dates et la catégorie", "who": "manager",
             "expect": {"state": "escalated", "availability_status": "available", "review_level": "manager"}},
            {"do": "decide", "action": "approve", "actor": "manager:Omar", "note": "Remise 10 % accordée (client régulier)", "label": "Omar approuve avec une remise notée", "who": "manager",
             "expect": {"state": "pending_customer", "review_note_contains": "10 %"}},
            {"do": "customer", "accepted": True, "label": "La famille confirme", "who": "client",
             "expect": {"state": "confirmed", "booking_created": True}},
        ],
    },
    {
        "key": "complaint-site",
        "title": "Réclamation — formulaire du site",
        "channel": "form", "customer": "Youssef T.",
        "message": "La voiture de la semaine dernière avait un problème de clim et personne ne répond.",
        "summary": "Une réclamation ne reçoit jamais de brouillon automatique : elle monte au manager en priorité haute, qui la traite et la clôture avec une note.",
        "proves": ["Intent complaint → escalade immédiate", "Aucun brouillon généré", "Priorité haute", "Clôture tracée par le manager"],
        "steps": [
            {"do": "public_intake", "label": "Envoyé depuis le formulaire public /demande", "who": "client",
             "expect": {"state": "escalated", "priority": "high", "review_level": "manager", "drafts_count": 0}},
            {"do": "decide", "action": "close", "actor": "manager:Omar", "note": "Client rappelé, geste commercial sur la prochaine location", "label": "Omar rappelle le client et clôture", "who": "manager",
             "expect": {"state": "closed", "review_note_contains": "rappelé"}},
        ],
    },
    {
        "key": "silent-lead-phone",
        "title": "Lead silencieux — appel téléphonique",
        "channel": "phone", "customer": "Sara M.",
        "message": "Bonjour, une berline automatique du 3 au 6 novembre à Agdal, merci.",
        "summary": "Le devis part, le client ne répond pas : relance n°1, relance n°2, puis le système signale un lead sans réponse et recommande un appel.",
        "proves": ["Politique de relance (24 h, max 2)", "Détection stalled à 72 h", "Recommandation d'appel", "Reprise du suivi après l'appel"],
        "steps": [
            {"do": "submit", "label": "Demande notée par téléphone", "who": "client",
             "expect": {"state": "quote_ready", "availability_status": "alternative"}},
            {"do": "decide", "action": "approve", "actor": "staff:Salma", "label": "Salma envoie la proposition", "who": "staff", "expect": {"state": "pending_customer"}},
            {"do": "advance", "hours": 25, "label": "+24 h : relance n°1 due", "who": "system", "expect": {"last_draft_kind": "reminder"}},
            {"do": "send_reminder", "actor": "staff:Salma", "label": "Salma envoie la relance n°1", "who": "staff", "expect": {"reminders_sent": 1}},
            {"do": "advance", "hours": 25, "label": "+24 h : relance n°2 due", "who": "system", "expect": {"reminders_sent": 1, "review_open": True}},
            {"do": "send_reminder", "actor": "staff:Salma", "label": "Salma envoie la relance n°2", "who": "staff", "expect": {"reminders_sent": 2}},
            {"do": "advance", "hours": 30, "label": "+30 h : toujours rien", "who": "system",
             "expect": {"state": "needs_human", "followup_action": "call", "events_include_state": "stalled"}},
            {"do": "stalled_action", "action": "call_done", "actor": "staff:Salma", "note": "Client joint, réfléchit jusqu'à demain", "label": "Salma appelle le client", "who": "staff",
             "expect": {"state": "pending_customer", "followups_scheduled": 1}},
        ],
    },
    {
        "key": "info-comptoir",
        "title": "Question d'information — comptoir",
        "channel": "walk-in", "customer": "Mehdi K.",
        "message": "Bonjour, quelle est la caution et le kilométrage inclus pour une berline ? Je passerai réserver plus tard.",
        "summary": "Pas de dates : le système prépare la question de clarification avec les infos utiles, l'équipe répond et le suivi démarre.",
        "proves": ["Intent info + champs manquants → clarification", "Brouillon de question prêt", "Aucune disponibilité calculée sans dates"],
        "steps": [
            {"do": "submit", "label": "Question posée au comptoir, saisie par l'équipe", "who": "client",
             "expect": {"state": "needs_human", "intent": "info", "last_draft_kind": "clarification", "availability_status": None}},
            {"do": "decide", "action": "approve", "actor": "staff:Youssef", "label": "Youssef envoie la réponse avec caution et km", "who": "staff",
             "expect": {"state": "pending_customer"}},
        ],
    },
    {
        "key": "reject-long-rental",
        "title": "Location longue durée — refus manager",
        "channel": "whatsapp", "customer": "Anas R.",
        "message": "Salam, un utilitaire du 1 au 25 novembre pour un chantier à Hay Riad, c'est possible ?",
        "summary": "25 jours > seuil automatique de 14 jours : le manager doit décider. Ici il refuse avec une raison, tout est tracé.",
        "proves": ["Règle max_auto_days → manager", "Refus tracé avec note", "Aucun envoi sans décision"],
        "steps": [
            {"do": "submit", "label": "Demande WhatsApp pour 25 jours", "who": "client",
             "expect": {"state": "escalated", "review_level": "manager", "review_reason_contains": "longue"}},
            {"do": "decide", "action": "reject", "actor": "manager:Omar", "note": "Flotte utilitaire réservée aux locations < 15 j en novembre", "label": "Omar refuse et explique", "who": "manager",
             "expect": {"state": "closed", "review_note_contains": "utilitaire"}},
        ],
    },
]


# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #
def _snapshot(rid: str) -> dict:
    with session() as db:
        r = db.get(Request, rid)
        drafts = db.query(Draft).filter_by(request_id=rid).order_by(Draft.id).all()
        fus = db.query(FollowUp).filter_by(request_id=rid).all()
        booking = db.query(Booking).filter_by(request_id=rid).first() is not None
        from .db import Event, Review
        events = [e.to_state for e in db.query(Event).filter_by(request_id=rid)]
        reviews = db.query(Review).filter_by(request_id=rid).order_by(Review.id).all()
        a = r.availability or {}
        return {
            "state": r.state, "intent": r.intent, "review_level": r.review_level, "priority": r.priority,
            "review_reason": r.review_reason or "", "flags": (r.structured or {}).get("flags", []),
            "availability_status": a.get("status"), "options": [o["vehicle_id"] for o in a.get("options", [])],
            "alternatives": [o["vehicle_id"] for o in a.get("alternatives", [])], "reasons": a.get("reasons", []),
            "drafts_count": len(drafts), "last_draft_kind": drafts[-1].kind if drafts else None,
            "last_draft_edited": drafts[-1].edited if drafts else False,
            "followups_scheduled": sum(1 for f in fus if f.status == "scheduled"),
            "reminders_sent": sum(1 for f in fus if f.status == "done"),
            "booking_created": booking, "events_states": events,
            "review_open": any(v.closed_at is None for v in reviews),
            "last_review_note": next((v.note for v in reversed(reviews) if v.note), ""),
            "followup_action": (r.followup or {}).get("action"),
        }


def _check(exp: dict, snap: dict) -> list[dict]:
    out = []
    for k, v in exp.items():
        if k == "options_include":
            ok, obs = v in snap["options"], snap["options"]
        elif k == "alternatives_include":
            ok, obs = v in snap["alternatives"], snap["alternatives"]
        elif k == "reasons_mention":
            ok, obs = any(v in r for r in snap["reasons"]), snap["reasons"][:2]
        elif k == "flags_include":
            ok, obs = all(f in snap["flags"] for f in v), snap["flags"]
        elif k == "review_note_contains":
            ok, obs = v in snap["last_review_note"], snap["last_review_note"]
        elif k == "review_reason_contains":
            ok, obs = v in snap["review_reason"], snap["review_reason"]
        elif k == "events_include_state":
            ok, obs = v in snap["events_states"], "présent" if v in snap["events_states"] else "absent"
        else:
            ok, obs = snap.get(k) == v, snap.get(k)
        out.append({"check": k, "expected": v, "observed": obs, "ok": bool(ok)})
    return out


def _apply(step: dict, sim: dict, rid: str | None) -> str:
    do = step["do"]
    if do in ("submit", "public_intake"):
        return orch.submit(sim["message"], sim["channel"], sim["customer"])
    assert rid
    if do == "decide":
        body = None
        if step.get("body_suffix"):
            with session() as db:
                r = db.get(Request, rid)
                body = (r.followup or {}).get("draft_fr", "") + step["body_suffix"]
        orch.resume(rid, {"action": step["action"], "actor": step.get("actor", "staff"), "note": step.get("note", ""),
                          "fields": step.get("fields", {}), "body": body})
    elif do == "customer":
        orch.customer_replied(rid, step["accepted"], "staff:Salma")
    elif do == "advance":
        clock.advance(step["hours"])
        orch.sweep()
    elif do == "send_reminder":
        orch.send_reminder(rid, step.get("actor", "staff"))
    elif do == "stalled_action":
        orch.staff_action_on_stalled(rid, step["action"], step.get("actor", "staff"), step.get("note", ""))
    else:
        raise ValueError(f"unknown step {do}")
    return rid


def run(key: str) -> dict:
    sim = next((s for s in SIMULATIONS if s["key"] == key), None)
    if not sim:
        raise KeyError(key)
    started = datetime.utcnow()
    rid, steps, all_ok = None, [], True
    for i, st in enumerate(sim["steps"]):
        t0 = time.perf_counter()
        error = None
        try:
            rid = _apply(st, sim, rid)
        except (ValueError, IllegalTransition, AssertionError) as exc:
            error = f"{type(exc).__name__}: {exc}"
        snap = _snapshot(rid) if rid else {}
        checks = _check(st.get("expect", {}), snap) if rid else []
        ok = error is None and all(c["ok"] for c in checks)
        all_ok &= ok
        steps.append({"i": i + 1, "label": st["label"], "who": st.get("who", "system"), "do": st["do"],
                      "detail": st.get("action") or (f"+{st['hours']} h" if st.get("hours") else ""),
                      "state": snap.get("state"), "checks": checks, "ok": ok, "error": error,
                      "ms": round((time.perf_counter() - t0) * 1000)})
        if error:
            break
    return {"key": key, "title": sim["title"], "channel": sim["channel"], "request_id": rid, "ok": all_ok,
            "steps": steps, "started_at": started.isoformat(timespec="seconds"),
            "clock": clock.now().isoformat(timespec="seconds")}


def catalogue() -> list[dict]:
    return [{k: v for k, v in s.items() if k != "steps"} | {"steps": [{"label": st["label"], "who": st.get("who", "system")} for st in s["steps"]]}
            for s in SIMULATIONS]

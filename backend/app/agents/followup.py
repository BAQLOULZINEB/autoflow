"""Follow-up Agent — « Relancer et suivre ».

Drafts the French reply (quote / alternative / clarification / reminder),
schedules the reminder policy and recommends the next best action.
Prices are *injected* from the availability result — never generated.
Recommendation only: staff executes.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from pydantic import BaseModel, Field

from ..rules import load_rules


class FollowUpOutput(BaseModel):
    draft_kind: str = "quote"            # quote | alternative | clarification | reminder | none
    draft_fr: str = ""
    action: str = "reply"                # reply | remind | call | escalate | close
    next_check_at: str | None = None
    reminder_no: int = 0
    rationale: str = ""
    sources: dict = Field(default_factory=dict)   # which fields fed the draft


def _fmt(d: str) -> str:
    return date.fromisoformat(d).strftime("%d/%m/%Y")


def _sign() -> str:
    return f"\n\n— {load_rules()['agency']['name']}"


def _fmt_opt(o: dict) -> str:
    tr = "automatique" if o["transmission"] == "automatique" else "manuelle"
    line = (f"• {o['model']} ({o['category']}, boîte {tr}) — {o['daily_rate_mad']} MAD/jour, "
            f"soit {o['total_mad']} MAD pour {o['days']} jour(s), départ {o['location']}")
    if o.get("note"):
        line += f" — {o['note']}"
    return line


def draft_quote(structured: dict, avail: dict, customer_name: str = "") -> FollowUpOutput:
    rules = load_rules()
    ag = rules["agency"]
    hello = f"Bonjour {customer_name}," if customer_name else "Bonjour,"
    p, r = structured["pickup_date"], structured["return_date"]
    out = FollowUpOutput(sources={"pickup_date": p, "return_date": r, "rate_source": "vehicles.daily_rate_mad"})
    if avail["status"] == "available":
        best = avail["options"][0]
        out.draft_kind = "quote"
        out.draft_fr = (f"{hello}\n\nMerci pour votre demande. Bonne nouvelle : nous avons un véhicule disponible "
                        f"du {_fmt(p)} au {_fmt(r)} :\n{_fmt_opt(best)}\n\n"
                        f"Caution : {ag['deposit_mad']} MAD · {ag['km_per_day']} km/jour inclus.\n"
                        f"Souhaitez-vous que nous bloquions ce véhicule pour vous ?" + _sign())
        out.rationale = f"Devis standard : {best['vehicle_id']} disponible, tarif de la table flotte."
    elif avail["status"] == "alternative":
        alts = avail["alternatives"][:2]
        out.draft_kind = "alternative"
        out.draft_fr = (f"{hello}\n\nMerci pour votre demande. Le véhicule exact demandé n'est pas disponible "
                        f"du {_fmt(p)} au {_fmt(r)}, mais nous pouvons vous proposer :\n" +
                        "\n".join(_fmt_opt(o) for o in alts) +
                        f"\n\nCaution : {ag['deposit_mad']} MAD · {ag['km_per_day']} km/jour inclus.\n"
                        f"L'une de ces options vous conviendrait-elle ?" + _sign())
        out.rationale = "Véhicule demandé indisponible ; alternatives proposées selon les règles de repli."
    else:
        out.draft_kind = "none"
        out.action = "escalate"
        out.rationale = "Aucune option : un membre de l'équipe doit répondre."
        return out
    fu = rules["follow_up"]
    out.action = "reply"
    out.reminder_no = 0
    out.next_check_at = None  # scheduled when staff actually sends
    return out


def draft_clarification(structured: dict, customer_name: str = "") -> FollowUpOutput:
    hello = f"Bonjour {customer_name}," if customer_name else "Bonjour,"
    txt = structured.get("clarification_fr") or (
        "Merci pour votre message ! Pourriez-vous nous préciser vos dates, la catégorie de véhicule et le lieu de prise en charge ?")
    txt = txt.replace("Bonjour et merci pour votre message !", "Merci pour votre message !")
    return FollowUpOutput(draft_kind="clarification", draft_fr=f"{hello}\n\n{txt}" + _sign(), action="reply",
                          rationale="Champs critiques manquants : question courte proposée.")


def schedule_after_send(now: datetime) -> str:
    fu = load_rules()["follow_up"]
    return (now + timedelta(hours=fu["first_reminder_after_h"])).isoformat(timespec="seconds")


def draft_reminder(structured: dict, reminder_no: int, customer_name: str = "") -> FollowUpOutput:
    hello = f"Bonjour {customer_name}," if customer_name else "Bonjour,"
    p = structured.get("pickup_date")
    when = f" pour le {_fmt(p)}" if p else ""
    body = (f"{hello}\n\nNous revenons vers vous concernant votre demande de location{when}. "
            f"Le véhicule proposé est toujours disponible pour le moment. Souhaitez-vous que nous le réservions ?"
            f"\nNous restons à votre disposition." + _sign())
    return FollowUpOutput(draft_kind="reminder", draft_fr=body, action="remind", reminder_no=reminder_no,
                          rationale=f"Relance n°{reminder_no} : aucune réponse client dans la fenêtre définie.")


def recommend_when_stalled(reminders_sent: int) -> FollowUpOutput:
    fu = load_rules()["follow_up"]
    n = f"{reminders_sent} relance(s) envoyée(s)" if reminders_sent else "aucune relance envoyée"
    return FollowUpOutput(draft_kind="none", action="call",
                          rationale=f"Aucune réponse après {fu['stale_after_h']} h ({n}) : appeler le client, puis clôturer si perdu.")

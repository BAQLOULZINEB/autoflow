"""Intake Agent evaluation — extraction accuracy against the labelled history.

Ground truth = `complete_fields` written by the dataset generator for every
message (the value the customer *meant*). We report per-field accuracy,
precision on the "needs a human" decision, and calibration of confidence.

Run from backend/:  python -m eval.eval_intake  [--llm]
Writes docs/../backend/eval/report.md
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

from app.agents.intake import run_intake
from app.rules import load_rules

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"


def main(use_llm: bool = False) -> None:
    hist = json.loads((DATA / "history.json").read_text(encoding="utf-8"))
    scen = json.loads((DATA / "scenarios.json").read_text(encoding="utf-8"))
    today = date(2026, 9, 21)
    rules = load_rules()

    fields = ("pickup_date", "return_date", "vehicle_category")
    hit = {f: 0 for f in fields}
    n_quote = 0
    intent_ok = 0
    routed_human_when_wrong = 0
    wrong_total = 0
    conf_bins: dict[str, list[int]] = {"<0.6": [0, 0], "0.6–0.8": [0, 0], "≥0.8": [0, 0]}
    rows = []

    for h in hist:
        received = today - timedelta(days=h["days_ago"])
        r = run_intake(h["message"], received, use_llm=use_llm)
        gt = h["complete_fields"]
        m = h["message"].lower()
        is_complaint = "problème" in m or "probleme" in m
        is_info = "caution" in m
        is_mod = "modifier" in m
        exp_intent = "complaint" if is_complaint else "info" if is_info else "modification" if is_mod else "quote"
        intent_ok += r.intent == exp_intent
        if exp_intent in ("quote", "modification"):
            n_quote += 1
            all_ok = True
            for f in fields:
                ok = getattr(r, f) == gt[f]
                hit[f] += ok
                all_ok &= ok
            # did the orchestrator's gate catch the mistakes?
            low = any(r.field_confidence.get(f, 0) < rules["critical_field_threshold"] for f in fields)
            routed = bool(r.missing_fields) or low or r.confidence < rules["confidence_threshold"]
            if not all_ok:
                wrong_total += 1
                routed_human_when_wrong += routed
            b = "<0.6" if r.confidence < 0.6 else "0.6–0.8" if r.confidence < 0.8 else "≥0.8"
            conf_bins[b][0] += all_ok
            conf_bins[b][1] += 1
            rows.append((h["message"][:70], r.intent, r.pickup_date, gt["pickup_date"], r.vehicle_category, gt["vehicle_category"], r.confidence, "→ humain" if routed else "auto"))

    lines = [f"# Évaluation de l'agent Intake — moteur `{'llm+rules' if use_llm else 'rules'}`", "",
             f"Jeu de test : {len(hist)} messages historiques (fictifs, étiquetés) + {len(scen)} scénarios de démo.", "",
             "## Exactitude par champ (demandes de devis / modification)", "",
             "| Champ | Exact | Total | Exactitude |", "|---|---|---|---|"]
    for f in fields:
        lines.append(f"| {f} | {hit[f]} | {n_quote} | {hit[f] / n_quote:.0%} |")
    lines += ["", f"Intention correcte : **{intent_ok}/{len(hist)} ({intent_ok / len(hist):.0%})**", "",
              "## Filet de sécurité de l'orchestrateur", "",
              f"Extractions avec au moins une erreur : **{wrong_total}** — dont routées vers un humain par les seuils : "
              f"**{routed_human_when_wrong}** ({(routed_human_when_wrong / wrong_total) if wrong_total else 1:.0%}).", "",
              "> Ce chiffre est le plus important : une erreur d'extraction qui atteint le client sans qu'une personne la voie est le vrai risque.", "",
              "## Calibration de la confiance", "", "| Confiance | Extractions 100 % correctes | Total | Taux |", "|---|---|---|---|"]
    for b, (ok, tot) in conf_bins.items():
        lines.append(f"| {b} | {ok} | {tot} | {(ok / tot) if tot else 0:.0%} |")
    lines += ["", "## Détail", "", "| Message | Intent | Date extraite | Date attendue | Cat. extraite | Cat. attendue | Conf. | Routage |", "|---|---|---|---|---|---|---|---|"]
    for row in rows:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    lines += ["", "## Limites", "",
              "- Étiquettes générées avec les messages (même générateur) : l'exactitude est **optimiste** ; un jeu de 30 messages réels annotés à la main est prévu en phase pilote.",
              "- Le moteur de règles ne couvre pas les formulations libres (« vers la fin du mois ») : elles tombent en `needs_human`, ce qui est le comportement voulu.",
              "- Aucun gain métier n'est déduit de ce rapport."]
    out = HERE / "report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:20]))
    print(f"\n→ {out}")


if __name__ == "__main__":
    main(use_llm="--llm" in sys.argv)

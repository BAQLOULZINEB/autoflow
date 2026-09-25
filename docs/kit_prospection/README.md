# Kit de proposition — Agence de location de voitures, Rabat

Package de conseil prêt pour la prospection : hypothèse d'audit, proposition visuelle, architecture supervisée, plan de démo, feuille d'exécution, étude de cas portfolio, prompt vidéo.

**Source de vérité :** [00_CONTEXT.md](00_CONTEXT.md). Aucun document ne doit le contredire.
**Règle d'intégrité :** aucun chiffre de résultat n'est écrit avant d'être mesuré. Tout ce qui n'est pas mesuré est étiqueté *hypothèse*.

## Arborescence

```
agence_location_rabat/
├── 00_CONTEXT.md                      Positionnement, architecture obligatoire, ton (source de vérité)
├── 01_prospect_brief_fr.md            Note de cadrage — hypothèse d'audit, pilote, prochaine étape
├── 02_workflow_audit_template_fr.md   Modèle d'audit (13 colonnes) + questions d'entretien
├── 03_solution_architecture_en.md     Architecture technique (EN) + résumé exécutif (FR)
├── 04_one_page_proposal_fr.md         Proposition une page (texte) — Problème → Système → Résultat
├── 05_diagram_brief.md                Index des visuels + 5 diagrammes Mermaid de base
├── 06_prospect_outreach_fr.md         LinkedIn · WhatsApp · Email · Relance J+3/5
├── 07_first_meeting_script_fr.md      Pitch 5 min · 10 questions · objections/réponses
├── 08_demo_plan.md                    Démo 7 min avec données simulées, scénarios A–E
├── 09_execution_plan.md               Phases 0–5 : objectif, sorties, risques, validation, livrables
├── 10_portfolio_case_study.md         Struggle → Architecture → System → Value + KPI transparents
├── 11_cinematic_video_prompt.md       Prompt vidéo 60 s + scènes + voix off
└── visuals/
    ├── 00_design_system.md            Palette sémantique, typo, grille, thème Mermaid, checklist
    ├── A_executive_one_page.md        Page A4 exécutive (PDF / WhatsApp / carrousel)
    ├── B_before_after_workflow_map.md Carte Avant / Après
    ├── C_multi_agent_architecture.md  Architecture (exécutive + technique)
    ├── D_employee_journey.md          Parcours employé — Salma
    ├── E_kpi_impact_board.md          Tableau KPI Avant / Objectif / Après (placeholders)
    └── F_pilot_roadmap.md             Feuille de route en 6 étapes + décision
```

## Ordre d'usage

| Moment | Documents |
|---|---|
| Préparer la prospection | 06 → 04 → visuals/A |
| Premier rendez-vous | 07 + visuals/A imprimé ; B, D, F en réserve |
| Audit sur site | 02 |
| Réponse écrite après RDV | 01 + 04 (PDF) + visuals/B |
| Jury / recruteurs | 03, 05, visuals/C, 10, 11 |
| Avant d'écrire du code | 09 (Phase 2 en premier), 08 |

## Rendu des diagrammes

```bash
npx -y @mermaid-js/mermaid-cli -i visuals/diagram.mmd -o visuals/diagram.svg -b "#FAF8F4" -w 1600
```

Le Mermaid fixe la structure ; la finition (typographie Manrope, grille, pictogrammes) se fait dans Figma/Canva à partir des specs de mise en page de chaque fichier `visuals/*.md`.

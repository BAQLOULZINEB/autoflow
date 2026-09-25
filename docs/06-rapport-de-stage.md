# 06 — Rapport de stage (structure et contenu)

**Titre :** AutoFlow — système d'automatisation intelligent des workflows d'entreprise. Application à une agence de location de voitures (Rabat).
**Intitulé du poste :** AI Engineer — automatisation des workflows métier.
**Sous-titre académique :** Architecture d'un système multi-agents supervisé (LangGraph) avec contrôle humain, traçabilité et évaluation.

> Chaque section renvoie vers le document du dossier qui la détaille. Les visuels de référence sont dans `assets/` ; les diagrammes exportables en PNG/PDF dans `diagrams/`.

---

## Remerciements · Résumé / Abstract

**Résumé (FR).** Les PME de services reçoivent leurs demandes clients par des canaux dispersés et les traitent à la main : re-saisie, vérifications lentes, relances oubliées, visibilité faible. Ce stage conçoit et réalise *AutoFlow*, un workflow supervisé qui structure les demandes, vérifie la disponibilité selon des règles, prépare réponses et relances, et transmet à une personne tout cas ambigu ou sensible. L'architecture est volontairement compacte — un orchestrateur LangGraph, trois agents spécialisés, un humain dans la boucle — et privilégie la fiabilité (aucune disponibilité inventée, chaque décision tracée) à l'autonomie. Le prototype est évalué sur 45 messages étiquetés : 89–91 % d'exactitude par champ, 100 % des erreurs rattrapées par la validation humaine. Les gains métier sont cadrés pour une mesure avant/après en pilote, sans chiffre promis.

**Abstract (EN).** Service SMEs receive customer requests across scattered channels and process them manually. This internship designs and builds *AutoFlow*, a supervised workflow that structures requests, checks availability deterministically, drafts replies and reminders, and hands every ambiguous or sensitive case to a human. The architecture is deliberately compact — one LangGraph orchestrator, three narrow agents, a human-in-the-loop gate — and favors reliability over autonomy. On 45 labeled messages the intake agent reaches 89–91 % per-field accuracy and 100 % of its errors are caught by the human gate. Business KPIs are framed for before/after measurement during a pilot, with no figure claimed in advance.

## 1. Introduction
1.1 Contexte de l'entreprise d'accueil et du marché (location de voitures au Maroc, canaux WhatsApp/Facebook, saisonnalité) — `kit_prospection/01_prospect_brief_fr.md`
1.2 Problématique : *comment automatiser le traitement des demandes sans retirer la décision aux humains ni inventer d'information ?*
1.3 Objectifs du stage et périmètre — `01-cahier-des-charges.md`
1.4 Démarche : audit (hypothèses) → cadrage → architecture → réalisation → évaluation → pilote — `kit_prospection/09_execution_plan.md`

## 2. État de l'art
2.1 Automatisation des workflows : RPA, low-code (n8n, Make), et limites face au langage naturel.
2.2 Agents LLM et orchestration : LangGraph, Microsoft Agent Framework, CrewAI/AutoGen ; notions de *state graph*, *checkpointing*, *human-in-the-loop*, *interrupt/resume*.
2.3 Extraction d'information structurée : sorties typées, *evidence-grounding*, calibration de confiance (référence : approche « probabilités, pas prose » de Jev AI).
2.4 Standards émergents : MCP (outils), A2A (agents), et leur pertinence pour une PME.
2.5 Synthèse : pourquoi un orchestrateur + agents étroits + humain — `03-choix-techniques.md`

## 3. Analyse et conception
3.1 Frictions observables et hypothèses d'audit (F1–F6) ; grille d'audit — `kit_prospection/02_workflow_audit_template_fr.md`
3.2 Exigences fonctionnelles RF1–RF10 et non fonctionnelles — `01-cahier-des-charges.md`
3.3 Architecture : vues contexte, conteneurs, composants, données, séquence, déploiement, défaillances — `02-architecture.md`, `diagrams/01-04*.html`
3.4 Machine à états (10 états) et matrice d'escalade (qui décide quoi)
3.5 Modèle de données et journal d'événements (auditabilité, KPI dérivés)

## 4. Réalisation
4.1 Orchestrateur LangGraph : nœuds, arêtes conditionnelles, `interrupt()`, `Command(goto)`, checkpointer — `backend/app/workflow/graph.py`
4.2 Agent Intake : grammaire de dates FR/darija, signaux typés, garde par preuve textuelle, LLM optionnel — `backend/app/agents/intake.py`
4.3 Agent Disponibilité : chevauchements, tampons, replis, raisons — `backend/app/agents/availability.py`
4.4 Agent Suivi : brouillons FR à prix injecté, politique de relance, détection de leads sans réponse — `backend/app/agents/followup.py`
4.5 API FastAPI et espace admin React : file de validation, fiche demande à 6 onglets, **Suivi en direct** (chemin allumé + règles évaluées), contrôles de démo
4.6 Données : générateur de jeu réaliste, rejeu de 6 semaines d'historique à travers le graphe — `04-demo-et-deploiement.md`
4.7 Intégration n8n et déploiement Vercel/Netlify + Docker

## 5. Évaluation
5.1 Tests end-to-end (8 scénarios) — `05-evaluation.md`
5.2 Exactitude de l'extraction et filet de sécurité (100 % des erreurs vers un humain) — `backend/eval/report.md`
5.3 Robustesse (LLM HS, redémarrage, transitions illégales, boucles)
5.4 Cadre de mesure des KPI métier et limites (Hawthorne, n faible, données simulées)

## 6. Discussion
6.1 Ce que le système fait bien / ne fait pas ; pourquoi l'escalade est une fonctionnalité
6.2 Coût réel pour une PME (≈ 0 MAD d'infrastructure, LLM optionnel) — `03-choix-techniques.md §3.8`
6.3 Généralisation : le même squelette (intake → vérification déterministe → brouillon → validation → suivi) s'applique à un cabinet, une clinique, un artisan — c'est le sens du titre *AutoFlow*
6.4 Perspectives : connecteur WhatsApp via n8n, outils MCP, jeu annoté réel, mesure pilote

## 7. Conclusion
Compétences mobilisées : architecture de workflows, systèmes multi-agents, ingénierie de prompts structurés, API, front, tests, évaluation, communication métier (kit de prospection).

## Annexes
A. Kit de prospection complet (`kit_prospection/`) · B. Visuels (`assets/`) · C. Diagrammes exportables (`diagrams/`) · D. Rapport d'évaluation (`backend/eval/report.md`) · E. Extrait du journal d'événements d'une demande · F. `rules.json` · G. Workflow n8n (`integrations/n8n/`)

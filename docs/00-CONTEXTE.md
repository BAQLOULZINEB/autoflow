# 00 — CONTEXTE.md · source de vérité du projet AutoFlow

> Ce fichier décrit *tout ce qu'il faut savoir* pour comprendre, présenter, défendre ou reprendre le projet : le pourquoi, le cadre, les décisions, l'état exact du système et le vocabulaire. Aucun autre document du dossier ne doit le contredire.
> Dernière mise à jour : 21 septembre 2026.

---

## 1. Fiche d'identité

| | |
|---|---|
| **Nom du projet** | AutoFlow — système d'automatisation intelligent des workflows d'entreprise |
| **Cadre** | Projet de stage — *AI Engineer, automatisation des workflows métier* |
| **Cas d'application** | Agence de location de voitures à Rabat (3 sites : Agdal, Hay Riad, aéroport Rabat-Salé) |
| **Auteur / posture** | Ingénieur IA & Architecte d'automatisation — « j'identifie les frictions opérationnelles des entreprises et je les transforme en workflows intelligents, systèmes multi-agents et outils d'aide à la décision simples à déployer » |
| **Statut** | V1 démontrable (2 commits, 16 tests verts). Données **fictives** générées ; aucun gain chiffré revendiqué avant mesure en pilote |
| **Dépôt** | `C:\Users\zineb\AutoFlow` — `backend/` (FastAPI + LangGraph), `frontend/` (React), `docs/` (ce dossier), `integrations/n8n/` |
| **Deux publics** | **Jury / professeurs** : rigueur d'ingénierie, architecture explicable, évaluation honnête. **Gérant d'agence** : outil clair, quasi gratuit à faire tourner, qui ne décide jamais à sa place |

## 2. Le problème (hypothèses d'audit, à valider sur site)

Une agence de location reçoit ses demandes par WhatsApp, Facebook, Instagram, téléphone, formulaire et comptoir. Le traitement est manuel et éclaté :

| # | Friction | Coût probable |
|---|---|---|
| F1 | Demandes dispersées sur plusieurs canaux | re-saisie, informations incomplètes, oublis |
| F2 | Disponibilité vérifiée à la main dans un tableau | réponses lentes, risque de double réservation |
| F3 | Questions répétitives (prix, caution, km, livraison) | attention de l'équipe consommée |
| F4 | Relances oubliées après devis | devis perdus sans que personne ne le voie |
| F5 | Statut des demandes flou (« qui gère ? où en est-on ? ») | coordination par messages et mémoire |
| F6 | Visibilité du gérant limitée | pilotage à l'instinct |

Ces frictions sont *probables*, pas *confirmées* : l'audit court (`kit_prospection/02_workflow_audit_template_fr.md`) sert à les vérifier et à mesurer une base avant/après.

## 3. La réponse : un workflow *supervisé*, pas un robot

**Promesse.** Réduire le travail répétitif, accélérer les réponses, garantir les relances, donner une vue simple — **en gardant l'équipe responsable de toute décision sensible**. Le système *prépare* ; une personne *décide et envoie*.

**Architecture obligatoire (compacte, volontairement).** 1 orchestrateur + 3 agents spécialisés + humain dans la boucle.

| Composant | Rôle métier | Rôle technique | Fichier |
|---|---|---|---|
| **Agent Intake** — *comprendre* | transforme le message en demande structurée, dit ce qui manque | règles (regex, grammaire de dates FR/darija) + LLM optionnel *gardé par la preuve* ; confiance par champ ; signaux typés | `backend/app/agents/intake.py` |
| **Agent Disponibilité** — *vérifier* | dit ce qui est libre, propose une alternative, explique | déterministe (chevauchement + tampon 4 h + maintenance + replis) ; **aucun LLM** | `backend/app/agents/availability.py` |
| **Agent Suivi** — *préparer* | brouillon FR, relance, prochaine action | templates avec prix injectés depuis la table ; politique 24 h / max 2 / 72 h | `backend/app/agents/followup.py` |
| **Orchestrateur** — *coordonner et sécuriser* | route, tient l'état, applique les règles, journalise, escalade | LangGraph `StateGraph`, machine à 10 états, matrice d'escalade, `interrupt()` / `Command`, checkpointer SQLite | `backend/app/workflow/graph.py` |
| **Humain** — *décider* | approuve, modifie, refuse, complète, appelle, clôture | file de validation équipe / manager dans l'espace admin | `frontend/src/pages/Queue.tsx`, `RequestDetail.tsx` |

**Trois invariants non négociables.**
1. Le système **n'envoie jamais** un message au client seul (l'envoi est un clic humain, simulé dans le pilote).
2. Il **n'invente jamais** une disponibilité (code déterministe) ni un champ (un champ LLM sans passage exact du message est rejeté).
3. **Tout est tracé** : chaque transition d'état écrit un événement (acteur, raison, horodatage) ; les KPI sont calculés depuis le journal, jamais stockés.

## 4. Périmètre

**Inclus (V1).** Saisie manuelle / formulaire public `/demande` / webhook n8n · 3 agents · orchestrateur · espace admin (tableau de bord, file à valider, suivi en direct avec raisonnement, simulations, demandes, flotte & règles, architecture) · jeu de données réaliste (24 véhicules, 80 réservations, 40 clients, 45 demandes sur 6 semaines rejouées) · 7 simulations métier jouables = tests d'acceptation · déploiement Vercel/Netlify + Docker/Render, ou Vercel Python.

**Exclu (audit-gated).** Paiement, tarification dynamique, envoi automatique, connecteur WhatsApp/Instagram réel, CRM/ERP, maintenance prédictive, voix, multi-agents « pour faire moderne ».

## 5. Décisions clés (et pourquoi)

| Décision | Raison courte | Détail |
|---|---|---|
| LangGraph plutôt que machine à états maison ou MS Agent Framework | HITL + checkpointing natifs, graphe lisible, 44 k projets dépendants ; MS AF = trop d'infra Azure pour un pilote | `03-choix-techniques.md §3.2` |
| Règles d'abord, LLM optionnel | la démo doit tourner hors ligne ; le gérant peut refuser tout appel externe | `§3.3` |
| Garde par la preuve (*evidence gate*) | anti-hallucination structurelle | `intake.py::extract_llm` |
| Signaux typés (probabilités, pas prose) | l'orchestrateur ne lit que des nombres comparés à `rules.json` (inspiration Jev AI) | `intake.py::_finalise` |
| Disponibilité sans LLM | argument n°1 de confiance pour le gérant | `availability.py` |
| SQLite → PostgreSQL par variable d'env | pilote sur laptop, cloud plus tard sans redesign | `db.py` |
| KPI dérivés du journal | auditables, jamais « déclarés » | `orchestrator.py::kpis` |
| Rejeu de l'historique à travers le vrai graphe | agence « vivante » à la démo sans une seule ligne écrite à la main | `orchestrator.py::replay_history` |
| Simulations = tests | un écart à l'écran = un test rouge ; a trouvé 2 vrais bugs | `simulations.py`, `tests/test_simulations.py` |
| n8n en périphérie seulement | colle vers les canaux ; il notifie, n'envoie jamais | `integrations/n8n/` |
| Charte navy / teal / crème, Manrope | continuité avec les documents déjà remis à l'agence | `frontend/src/index.css` |

## 6. État exact du système (V1)

**Chiffres vérifiés** (reproductibles : `pytest -q`, `python -m eval.eval_intake`, premier démarrage).

| Mesure | Valeur |
|---|---|
| Tests automatisés | 16 (8 e2e scénarios A–E + 7 simulations + catalogue), tous verts |
| Exactitude Intake (45 messages étiquetés, moteur règles) | dates 89 % / 82 %, catégorie 91 %, intention 100 % |
| Extractions erronées routées vers un humain | 8/8 (100 %) |
| Calibration | confiance ≥ 0,8 → 94 % entièrement correctes ; < 0,8 → 0 % |
| Historique rejoué au démarrage | 45 demandes, ~370 événements, 22 confirmées, 16 clôturées, 7 leads à rappeler, 7 relances envoyées, ≈ 5 s |
| Routes API | 24 (`/api/health`, `/api/public/intake`, requests, decision, trace, live, reviews, fleet, rules, kpis, events, graph, simulations, demo) |
| Code métier | ≈ 1 400 lignes Python, ≈ 1 600 lignes TS/TSX |

**Machine à états.** `new → incomplete → checked → quote_ready → pending_customer → stalled → needs_human → escalated → confirmed → closed` (transitions légales dans `db.py::TRANSITIONS`).

**Matrice d'escalade** (`graph.py::decide_after_availability`). Vers l'humain si : réclamation ; champs manquants ; confiance globale < 0,75 ou champ critique < 0,7 ; remise demandée (→ manager) ; client régulier + alternative ; durée > 14 j (→ manager) ; valeur > 6 000 MAD (→ manager) ; invalide / indisponible ; > 8 sauts.

**Écrans de l'espace admin.** Tableau de bord · File à valider (manager / équipe) · Suivi en direct (flux + chemin allumé + règles évaluées) · Simulations · Demandes · Fiche demande (Raisonnement, Structurée, Disponibilité, Brouillon, Relance, Journal + panneau de décision) · Nouvelle demande · Flotte & règles · Architecture · `/demande` public · Mode présentation.

## 7. Modèle économique pour l'agence

Infrastructure ≈ 0 MAD (laptop, ou offres gratuites Vercel + Render + Neon) · LLM optionnel ≈ 0,005–0,02 MAD/demande ou Ollama local = 0 · licences 0 (MIT/Apache). La valeur facturable est le **temps d'audit et d'adaptation**, jamais une licence. Les gains sont **mesurés** en pilote (base avant/après), pas promis.

## 8. Ressources et inspirations utilisées

- Kit de prospection (11 documents + visuels), infographies et propositions PDF : `kit_prospection/`, `assets/`.
- Open source : LangGraph (workflow persistant, HITL), `langgraph-customer-support-agent` (structure agent/tools/state/prompts), `langgraph-hitl-fastapi-demo` (approuver/modifier/refuser), Awesome n8n Templates (relances/notifications), Microsoft Agent Framework (veille « entreprise »).
- Jev AI (TypeSafe) : « décisions typées avec probabilité calibrée, pas de prose » → `signals`.
- Skills de production : *architecture-mapper* (7 vues), *diagram-design* (4 diagrammes HTML+SVG dark), *ui-ux-pro-max* (icônes SVG, transitions, focus, reduced-motion, mode présentation).

## 9. Glossaire

| Terme | Sens dans ce projet |
|---|---|
| **Workflow supervisé** | pipeline automatisé dont chaque sortie vers le client passe par une personne |
| **Orchestrateur** | le graphe LangGraph : route, tient l'état, applique les règles, journalise, escalade ; ne prend aucune décision commerciale |
| **Agent** | fonction spécialisée à responsabilité unique (Intake, Disponibilité, Suivi) ; *propose*, ne décide pas |
| **HITL / interrupt** | point où l'exécution se suspend (persistée) jusqu'à une décision humaine ; reprise par `Command(resume=…)` |
| **Evidence gate** | un champ extrait par LLM n'est gardé que si son passage justificatif est dans le message |
| **Signaux** | questions oui/non typées avec probabilité (`is_complaint`, `discount_requested`, `dates_ambiguous`…) |
| **Matrice d'escalade** | table règle → niveau (équipe / manager) → état |
| **Sweep** | balayage des relances dues et des leads sans réponse, à chaque chargement du dashboard |
| **Horloge démo** | décalage stocké en base pour « avancer » le temps (+24 h, +72 h) et rejouer l'historique |
| **Simulation** | cas métier scripté, joué à travers la vraie API, avec assertions par étape |
| **Trace de décision** | reconstruction lisible du chemin suivi et de chaque règle évaluée (`explain.py`) |

## 10. Prochaines étapes

1. Audit sur site → base KPI « avant » (≥ 5 mesures par indicateur).
2. Jeu de 30 messages réels annotés → ré-évaluation de l'Intake, activation éventuelle du LLM.
3. Connecteur WhatsApp Business **via n8n** (notification seulement).
4. Pilote 2–4 semaines → tableau avant/après, limites déclarées, décision du gérant.
5. Généralisation : même squelette pour un cabinet, une clinique, un artisan (c'est le sens du nom *AutoFlow*).

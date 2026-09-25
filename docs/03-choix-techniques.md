# 03 — Choix techniques et état de l'art (septembre 2026)

## 3.1 Principe directeur

> **Simplicité d'abord.** Un workflow orchestré avec 3 agents et 6 outils métier est plus crédible, plus testable et plus démontrable que « 5 agents pour faire moderne ».

Chaque choix ci-dessous est un *decision record* : contexte → option retenue → alternatives écartées → coût de retour arrière.

## 3.2 Orchestration : LangGraph 1.2

| | |
|---|---|
| **Contexte** | Il faut un workflow *persistant* qui se met en pause pour une décision humaine, reprend des jours plus tard, et dont chaque étape est traçable. |
| **Choix** | `langgraph.StateGraph` + `interrupt()` / `Command(resume=…)` + checkpointer `SqliteSaver`. Un thread par demande (`thread_id = request_id`). |
| **Pourquoi** | ~42 k ★, 44 k projets dépendants, human-in-the-loop et checkpointing natifs ; le graphe est *lisible* (`GET /api/graph` le dessine) ; `Command(goto=…)` permet à l'humain de renvoyer vers `availability` après complétion. |
| **Alternatives** | *Machine à états maison* : moins de dépendances mais il faut réécrire persistance + reprise + interruption. *Microsoft Agent Framework* (13,6 k ★, Python/.NET/Go, observabilité, checkpointing) : très prometteur pour une version « entreprise », mais l'infrastructure Azure consommerait le temps du pilote. *CrewAI / AutoGen* : orientés conversation multi-agents, pas machine à états explicite. *n8n seul* : excellent pour la colle canaux/notifications, faible pour l'état métier et les règles. |
| **Coût de retour** | Faible : les agents sont des fonctions Python pures ; `graph.py` fait 200 lignes. |

## 3.3 Extraction : règles d'abord, LLM optionnel et *gardé par la preuve*

| | |
|---|---|
| **Contexte** | Les messages sont courts, en français / darija, avec des dates dans 6 formats. Le propriétaire peut refuser tout appel externe. |
| **Choix** | Moteur de règles (regex + grammaire de dates FR) toujours exécuté. LLM (Anthropic / OpenAI / Ollama via `init` LangChain, `with_structured_output`) activable par variable d'env. **Un champ LLM n'est conservé que si son `evidence` est une sous-chaîne exacte du message.** |
| **Inspiration** | *Jev AI* (TypeSafe) — « des décisions typées avec une probabilité calibrée, pas de la prose ». AutoFlow expose `signals = {is_complaint: 0.9, discount_requested: 0.95, dates_ambiguous: 0.45, …}` : l'orchestrateur ne lit jamais du texte libre, seulement des nombres comparés à `rules.json`. |
| **Alternatives** | LLM seul : hallucination possible, coût, latence, dépendance réseau. NER fine-tuné : pas de données annotées avant le pilote. |
| **Mesure** | `backend/eval/report.md` : dates 89 % / 82 %, catégorie 91 %, intention 100 %, **100 % des extractions erronées routées vers un humain**. |

## 3.4 Disponibilité : déterministe, sans LLM

Chevauchement de dates + tampon 4 h + maintenance + règles de repli (`category_fallbacks`, `shift_days_allowed`). Chaque exclusion porte une raison lisible. *Inventer une disponibilité est structurellement impossible* — c'est l'argument n°1 pour la confiance du gérant.

## 3.5 Persistance : SQLAlchemy 2 + SQLite → PostgreSQL

Un pilote doit tourner sur un laptop sans installation. `DATABASE_URL=postgresql+psycopg://…` bascule sur Neon/Supabase sans changer une ligne. Les KPI sont des requêtes sur `events` (horodatages), jamais des nombres stockés : auditables.

## 3.6 API + interface : FastAPI + React/Vite

FastAPI : schémas Pydantic partagés avec les agents, OpenAPI gratuit (`/docs`). React + Vite : build statique déployable sur Vercel/Netlify, zéro secret côté client. Pas de Tailwind ni d'UI kit : 250 lignes de CSS avec les tokens du kit de prospection (navy / teal / crème) — l'agence reconnaît la charte des documents qu'elle a reçus.

Le panneau **Suivi en direct** rend le graphe en SVG inline (palette *diagram-design*) et allume le chemin réellement suivi ; le tableau de raisonnement liste chaque règle évaluée (valeur, seuil, branche). Le jury voit *pourquoi* ; le gérant voit *qu'une personne décide*.

## 3.7 Intégrations : n8n en périphérie, MCP/A2A en veille

- **n8n** (280+ templates communautaires) : webhook WhatsApp/Typeform → `POST /api/public/intake` → notification Slack/WhatsApp de l'équipe. n8n *notifie*, n'envoie jamais au client.
- **MCP (Model Context Protocol)** : si le pilote passe à un LLM avec outils, exposer `check_vehicle_availability` et `schedule_follow_up` comme serveurs MCP est la voie standard 2026 ; hors périmètre du pilote.
- **A2A** : inutile à 1 orchestrateur.

## 3.8 Modèle de coût pour l'agence

| Poste | Pilote | Après pilote |
|---|---|---|
| Hébergement | 0 MAD (laptop) ou offres gratuites Vercel + Render + Neon | ~5–7 $/mois si instance dédiée |
| LLM | 0 MAD (`LLM_PROVIDER=none`) | optionnel : ~0,005–0,02 MAD / demande (Haiku 4.5 / Sonnet 5, quelques centaines de tokens) ; ou Ollama local = 0 |
| Licences | 0 (MIT/Apache : LangGraph, FastAPI, React, n8n community) | 0 |
| Temps équipe | 30 min de prise en main | — |

Positionnement : **un outil quasi gratuit à faire tourner, facturé sur le temps d'audit et d'adaptation, jamais sur une licence.**

## 3.9 Ce que nous avons volontairement exclu

Paiement, tarification dynamique, envoi automatique, connecteur WhatsApp réel, CRM, maintenance prédictive, voix. Chacun est *audit-gated* : il n'entre que si l'observation sur site prouve son besoin.

# 02 — Architecture d'AutoFlow

> Vues produites selon la méthode *architecture-mapper* : une question par diagramme, jamais tout le système sur un seul schéma.
> Convention : trait plein = **FACT** (vérifié dans le code) · trait pointillé = **HYPOTHESIS** (futur / à valider avec l'agence).

## 2.1 Vue contexte — qui parle au système ?

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Manrope, Inter, system-ui","lineColor":"#0E9C99","primaryColor":"#FFFFFF","primaryBorderColor":"#D8DCE3","primaryTextColor":"#111827"}}}%%
flowchart LR
    classDef human fill:#0B1F3A,color:#fff,stroke:#0B1F3A
    classDef sys fill:#DDF3F2,color:#0B1F3A,stroke:#0E9C99,stroke-width:2px
    classDef ext fill:#fff,color:#111827,stroke:#D8DCE3,stroke-dasharray:4 4

    Client[Client<br/>WhatsApp · Facebook · formulaire · comptoir]:::human
    Staff[Équipe agence<br/>Salma · Youssef]:::human
    Manager[Manager<br/>Omar]:::human
    AF[(AutoFlow<br/>workflow supervisé)]:::sys
    LLM[Fournisseur LLM<br/>Anthropic / OpenAI / Ollama]:::ext
    N8N[n8n<br/>webhooks & notifications]:::ext
    WA[WhatsApp Business API]:::ext

    Client -->|message texte| AF
    Client -->|formulaire /demande| AF
    Staff -->|valide · modifie · envoie| AF
    Manager -->|décide prix · réclamations| AF
    AF -->|brouillons · file · KPI| Staff
    AF -->|escalades| Manager
    AF -.->|extraction optionnelle<br/>texte du message seulement| LLM
    N8N -.->|POST /api/public/intake| AF
    WA -.->|via n8n, futur| N8N
```

**Frontière clé (FACT)** : AutoFlow n'envoie jamais un message au client. Il produit des brouillons ; une personne clique « envoyer ».

## 2.2 Vue conteneurs — de quoi est fait le système ?

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Manrope, Inter, system-ui","lineColor":"#0E9C99","primaryColor":"#FFFFFF","primaryBorderColor":"#D8DCE3","primaryTextColor":"#111827"}}}%%
flowchart TB
    classDef fe fill:#EDE9FE,color:#3B0764,stroke:#7C3AED
    classDef be fill:#DDF3F2,color:#0B1F3A,stroke:#0E9C99
    classDef db fill:#FEF3C7,color:#78350F,stroke:#F59E0B
    classDef ext fill:#fff,color:#111827,stroke:#D8DCE3,stroke-dasharray:4 4

    subgraph Vercel_Netlify["Vercel / Netlify (statique)"]
        WEB[Espace admin<br/>React + Vite + TS<br/>/login /queue /requests/:id /architecture /demande]:::fe
    end
    subgraph Backend["Backend Python (Docker · Render · Vercel Python)"]
        API[FastAPI<br/>app/main.py<br/>auth X-Admin-Token · CORS]:::be
        ORCH[Orchestrateur LangGraph<br/>workflow/graph.py<br/>StateGraph · interrupt · Command]:::be
        AG1[Agent Intake<br/>agents/intake.py<br/>règles + LLM optionnel]:::be
        AG2[Agent Disponibilité<br/>agents/availability.py<br/>déterministe]:::be
        AG3[Agent Suivi<br/>agents/followup.py<br/>brouillons · relances]:::be
        SVC[Service orchestrator.py<br/>submit · resume · sweep · kpis · seed]:::be
        RULES[rules.json<br/>règles métier versionnées]:::db
        DB[(SQLite / PostgreSQL<br/>requests · events · drafts<br/>reviews · follow_ups · fleet)]:::db
        CKPT[(checkpoints.db<br/>LangGraph SqliteSaver)]:::db
    end
    LLM[LLM API]:::ext

    WEB -->|HTTPS JSON /api/*| API
    API --> SVC --> ORCH
    ORCH --> AG1 & AG2 & AG3
    AG1 -.->|with_structured_output| LLM
    AG2 --> RULES
    AG3 --> RULES
    ORCH -->|store.transition → Event| DB
    ORCH -->|thread_id = request_id| CKPT
    SVC --> DB
```

## 2.3 Vue composants — le graphe LangGraph

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Manrope, Inter, system-ui","lineColor":"#0E9C99","primaryColor":"#FFFFFF","primaryBorderColor":"#D8DCE3","primaryTextColor":"#111827"}}}%%
flowchart TD
    classDef node fill:#DDF3F2,color:#0B1F3A,stroke:#0E9C99
    classDef gate fill:#0B1F3A,color:#fff,stroke:#0E9C99,stroke-width:2px
    classDef cond fill:#fff,color:#111827,stroke:#D8DCE3

    S((START)) --> intake[intake<br/>run_intake → structured]:::node
    intake --> r1{route_after_intake}:::cond
    r1 -->|intent = complaint| escalate[escalate<br/>→ escalated · manager · high]:::node
    r1 -->|manquants · conf < 0.75 · champ < 0.7| clarify[clarify<br/>brouillon question → needs_human]:::node
    r1 -->|complète & confiante| availability[availability<br/>check_availability → checked]:::node
    availability --> r2{decide_after_availability<br/>matrice d'escalade}:::cond
    r2 -->|remise · VIP+alt · > 14 j · > 6000 MAD<br/>invalide · indisponible · hops > 8| sensitive[sensitive<br/>→ needs_human / escalated]:::node
    r2 -->|cas standard| draft[draft<br/>draft_quote → quote_ready]:::node
    escalate & clarify & sensitive & draft --> hr[human_review<br/>interrupt payload]:::gate
    hr -->|Command resume: approve · edit · reject · close| finalize[finalize<br/>envoi simulé · relance planifiée<br/>→ pending_customer / closed]:::node
    hr -->|Command goto: complete + fields| availability
    finalize --> E((END))
```

Le graphe réel est exposé par `GET /api/graph` (`draw_mermaid()`) et affiché dans l'onglet *Architecture* de l'espace admin — le diagramme et le code ne peuvent pas diverger.

## 2.4 Vue flux de données — que devient un message ?

```text
Message brut (str, fr/darija)
  → Intake : normalisation NFD · regex dates FR · mots-clés · [LLM structured output + preuve verbatim]
  → StructuredRequest {intent, dates ISO, catégorie, boîte, lieux, flags[], field_confidence{}, confidence, missing[], evidence{}}
  → Orchestrateur : seuils (rules.json) → route
  → Disponibilité : SELECT vehicles, bookings → chevauchement + tampon 4 h + maintenance → AvailabilityResult {status, options[], alternatives[], reasons[]}
  → Matrice d'escalade (règles) → review {level, priority, reason}
  → Suivi : template FR + injection prix depuis la table (jamais généré) → FollowUpOutput {draft_kind, draft_fr, action}
  → interrupt() : payload persisté (checkpoint) ; DB : Request.state, Draft, Review, Event
  → Décision humaine (JSON) → Command(resume) → finalize : Draft.sent_at, FollowUp.due_at = now + 24 h, Event
  → Sweep (à chaque chargement du dashboard) : FollowUp due → brouillon relance ; > 72 h → stalled → needs_human
  → KPI = agrégats sur events/drafts/follow_ups (jamais stockés)
```

## 2.5 Vue séquence — scénario C (ambiguë + remise)

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Manrope, Inter, system-ui","lineColor":"#0E9C99"}}}%%
sequenceDiagram
    autonumber
    participant W as Espace admin
    participant API as FastAPI
    participant G as LangGraph
    participant I as Intake
    participant A as Disponibilité
    participant DB as SQLite (events)
    participant M as Manager (Omar)

    W->>API: POST /api/demo/load/C
    API->>DB: INSERT Request(new) + Event
    API->>G: invoke(thread=A-0003)
    G->>I: run_intake("...week-end prochain... geste sur le prix")
    I-->>G: dates conf 0.55 · catégorie null · flags[ambiguous_dates, discount_requested, vip_claimed]
    G->>G: route_after_intake → clarify
    G->>DB: Draft(clarification) · new→incomplete→needs_human · Review(manager, high)
    G-->>API: interrupt(payload)
    API-->>W: state=needs_human, pending_interrupt
    M->>W: complète dates 24→26/10, catégorie citadine
    W->>API: POST /decision {action: complete, fields}
    API->>G: invoke(Command(resume))
    G->>G: human_review → Command(goto=availability)
    G->>A: check_availability(structured complété)
    A-->>G: available · CIT-03 · 2 j · 460 MAD
    G->>G: decide_after_availability → sensitive (remise)
    G->>DB: checked→escalated · Draft(quote) · Review(manager)
    G-->>API: interrupt(payload)
    M->>W: approuve, note "remise 10 % accordée"
    W->>API: POST /decision {action: approve}
    G->>DB: escalated→quote_ready→pending_customer · Draft.sent · FollowUp(+24 h)
    G-->>API: END
```

## 2.6 Vue déploiement

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Manrope, Inter, system-ui","lineColor":"#0E9C99"}}}%%
flowchart LR
    classDef host fill:#fff,stroke:#0B1F3A,color:#0B1F3A
    classDef proc fill:#DDF3F2,stroke:#0E9C99,color:#0B1F3A
    classDef vol fill:#FEF3C7,stroke:#F59E0B,color:#78350F

    subgraph Dev["Poste de dev / démo agence (laptop)"]
        V[vite dev :5173<br/>proxy /api → :8000]:::proc
        U[uvicorn :8000]:::proc
        F1[(autoflow.db · checkpoints.db)]:::vol
        U --- F1
    end
    subgraph Cloud["Option cloud (pilote distant)"]
        VC[Vercel / Netlify<br/>frontend/dist<br/>VITE_API_URL]:::host
        RD[Render / Railway / Fly<br/>Docker backend/<br/>volume /data]:::host
        PG[(Neon / Supabase Postgres<br/>DATABASE_URL, optionnel)]:::vol
        VC -->|HTTPS + X-Admin-Token| RD
        RD -.-> PG
    end
    subgraph Serverless["Option tout-Vercel"]
        VP[Vercel Python<br/>backend/api/index.py<br/>DB dans /tmp = éphémère]:::host
    end
```

Secrets : `ADMIN_TOKEN`, clés LLM — variables d'environnement uniquement, jamais dans le code. Le frontend ne contient aucun secret : le token est saisi à la connexion.

## 2.7 Vue défaillances — que se passe-t-il quand ça casse ?

| Défaillance | Détection | Comportement | Chemin de secours | Visible par |
|---|---|---|---|---|
| LLM indisponible / clé invalide | exception dans `extract_llm` | flag `llm_failed:*`, confiance × 0.9, résultat des règles conservé | rules-only (toujours calculé) | onglet Structurée (`engine`) |
| LLM invente un champ | preuve absente du message | champ rejeté (`null`), confiance 0 | question de clarification | flags / manquants |
| Dates ambiguës (« week-end prochain ») | conf 0.55 < 0.7 | `needs_human` + brouillon de question | staff complète → `Command(goto=availability)` | file à valider |
| Table flotte périmée | `fleet_snapshot_at` sur chaque résultat | résultat horodaté | staff relit avant envoi | onglet Disponibilité |
| Crash pendant le workflow | checkpoint LangGraph par nœud | reprise au dernier nœud persisté | `graph.get_state(thread)` | — |
| Boucle agents | `hops > MAX_HOPS (8)` | route `sensitive` → humain | — | raison de revue |
| Transition illégale | `TRANSITIONS` dans `store.transition` | `IllegalTransition` → HTTP 409 | — | message d'erreur UI |
| Trop de relances | `max_reminders = 2` | plus de planification, `stalled` → appel recommandé | staff clôture | onglet Relance |
| Demande orpheline | toute demande est dans un état de `STATES` ; KPI `by_state` couvre 100 % | — | — | tableau de bord |

## 2.8 Inventaire d'architecture

| Élément | Responsabilité | Interface | Données possédées | Techno | Dépend de | Impact si HS | Preuve |
|---|---|---|---|---|---|---|---|
| Espace admin | file, décisions, KPI, démo | HTTP JSON | token (localStorage) | React 19, Vite, TS, mermaid | API | plus de validation humaine possible | `frontend/src` |
| FastAPI | auth, routes, sérialisation | REST `/api/*` | — | FastAPI 0.141 | service, DB | tout | `backend/app/main.py` |
| Orchestrateur | routage, états, interrupt, matrice d'escalade | `invoke`, `Command` | checkpoints | LangGraph 1.2 | agents, store, rules | workflow figé | `workflow/graph.py` |
| Intake | message → structuré + preuves | `run_intake()` | — | regex/unicodedata, LangChain optionnel | LLM (opt.) | tout passe en `needs_human` | `agents/intake.py` |
| Disponibilité | options/alternatives/raisons | `check_availability()` | — | Python pur | vehicles, bookings, rules | pas de devis | `agents/availability.py` |
| Suivi | brouillons FR, relances, action | `draft_*`, `recommend_*` | — | templates | rules | pas de brouillon | `agents/followup.py` |
| Store | transitions légales + journal | `transition/log/…` | events, drafts, reviews, follow_ups | SQLAlchemy 2 | DB | perte de traçabilité | `workflow/store.py` |
| Règles | seuils, replis, politique de relance | `load_rules()` | rules.json | JSON | — | valeurs par défaut | `rules.py`, `data/rules.json` |
| Horloge démo | temps contrôlable | `now()/advance()` | settings | — | DB | relances non testables | `clock.py` |

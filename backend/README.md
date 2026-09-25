# AutoFlow backend

FastAPI + LangGraph. Voir `../docs/02-architecture.md` pour les vues et `../docs/04-demo-et-deploiement.md` pour lancer.

```
app/
├── main.py               routes (auth X-Admin-Token), /api/live, /api/requests/{id}/trace
├── config.py · db.py · clock.py · rules.py
├── agents/               intake.py (règles + LLM evidence-gated) · availability.py (déterministe) · followup.py
└── workflow/
    ├── graph.py          StateGraph · interrupt() · Command(goto) · checkpointer SQLite
    ├── orchestrator.py   submit · resume · sweep · kpis · reset_and_seed · replay_history
    ├── store.py          transitions légales + journal d'événements
    ├── explain.py        trace de décision (panneau « Suivi en direct »)
    └── state.py
data/                     generate_dataset.py → fleet/bookings/customers/history/scenarios
tests/                    8 tests e2e · eval/eval_intake.py → eval/report.md
```

Env : `LLM_PROVIDER=none|anthropic|openai|ollama`, `ADMIN_TOKEN`, `CORS_ORIGINS`, `DATABASE_URL`, `SEED_DEMO`.

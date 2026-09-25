# Deploy AutoFlow Pro on Vercel

Single Vercel project — frontend (Vite/React) + backend (FastAPI on Python serverless), same origin.

## Steps

1. On https://vercel.com → **Add New… → Project → Import** the GitHub repo `BAQLOULZINEB/autoflow`.
2. Vercel auto-detects the root `vercel.json`. Leave framework/build settings as-is (they are overridden by `vercel.json`).
3. Set **Environment Variables** (Project → Settings → Environment Variables):
   - `ADMIN_TOKEN` — the admin token (default in code: `change-me-admin`)
   - `CORS_ORIGINS` — `*` (or the Vercel URL)
   - `SEED_DEMO` — `true` for first deploy to seed fictional data; set to `false` afterwards
   - `LLM_PROVIDER` — `none` (rules-only) or `anthropic` / `openai`
   - `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` — only if using an LLM provider
   - `DATABASE_URL` — leave empty to use `/tmp` SQLite (ephemeral); set a `postgresql://` URL for persistence
4. Click **Deploy**.

## Local dev (same as before)

Backend:
```
cd backend
../.venv/Scripts/python -m uvicorn app.main:app --port 8000
```
Frontend:
```
cd frontend
npm install
npm run dev
```
Frontend proxies `/api` → `http://localhost:8000` via Vite dev server.

## Notes

- Vercel serverless filesystem is read-only outside `/tmp`, so the default SQLite DB and LangGraph checkpoint DB live in `/tmp` and reset on cold starts. Use a real Postgres URL via `DATABASE_URL` for persistent state.
- Frontend calls `/api/*` on the same origin — no `VITE_API_URL` needed on Vercel.
- The vehicle-image cache under `backend/data/vehicle_image_cache/` is regenerated at runtime and gitignored.

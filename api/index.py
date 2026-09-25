"""Vercel Python serverless entry (root-level).

Vercel auto-detects `/api/*.py` as serverless functions at the repo root.
This file exposes the FastAPI app under /api/*. Backend code lives in `backend/`,
so we add it to sys.path before importing. Serverless FS is read-only except /tmp,
so pilot DB and checkpoints live in /tmp (ephemeral).

For persistence, set DATABASE_URL=postgresql://... in the Vercel project.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND = os.path.join(_ROOT, "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/autoflow.db")
os.environ.setdefault("CHECKPOINT_DB", "/tmp/checkpoints.db")
os.environ.setdefault("CORS_ORIGINS", "*")

from app.main import app  # noqa: E402,F401

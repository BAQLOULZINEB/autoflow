"""Vercel Python serverless entry. Serverless FS is read-only except /tmp, so the
pilot DB lives in /tmp (ephemeral — use DATABASE_URL=postgresql://... for persistence)."""
import os
os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/autoflow.db")
os.environ.setdefault("CHECKPOINT_DB", "/tmp/checkpoints.db")
from app.main import app  # noqa: E402,F401

"""Vercel Python serverless entry (root-level)."""
import os
import sys
import traceback

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND = os.path.join(_ROOT, "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/autoflow.db")
os.environ.setdefault("CHECKPOINT_DB", "/tmp/checkpoints.db")
os.environ.setdefault("CORS_ORIGINS", "*")

_import_error: str | None = None
try:
    from app.main import app  # noqa: F401
except Exception:
    _import_error = traceback.format_exc()
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/{full_path:path}")
    def _report(full_path: str):
        return {
            "error": "Backend import failed",
            "trace": _import_error,
            "cwd": os.getcwd(),
            "backend_path": _BACKEND,
            "backend_exists": os.path.isdir(_BACKEND),
            "listing_root": sorted(os.listdir(_ROOT))[:40] if os.path.isdir(_ROOT) else None,
            "listing_backend": sorted(os.listdir(_BACKEND))[:40] if os.path.isdir(_BACKEND) else None,
            "sys_path": sys.path[:10],
        }

    @app.post("/{full_path:path}")
    def _report_post(full_path: str):
        return _report(full_path)

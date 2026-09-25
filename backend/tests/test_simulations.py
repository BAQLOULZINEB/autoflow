"""Every built-in simulation must pass end to end — this is the product's acceptance suite."""
import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_sims.db"
os.environ["CHECKPOINT_DB"] = "./test_sims_ckpt.db"
os.environ["LLM_PROVIDER"] = "none"
os.environ["ADMIN_TOKEN"] = "test-autoflow-token"

import pytest
from fastapi.testclient import TestClient

from app import simulations as sims
from app.main import app
from app.workflow import orchestrator as o

H = {"X-Admin-Token": os.environ["ADMIN_TOKEN"]}


@pytest.fixture(scope="module")
def client():
    o.reset_and_seed(with_history=False)
    with TestClient(app) as c:
        yield c
    from app.db import get_engine
    from app.workflow.graph import get_graph
    get_engine().dispose(); get_graph.cache_clear()
    for f in ("test_sims.db", "test_sims_ckpt.db"):
        try:
            Path(f).unlink(missing_ok=True)
        except PermissionError:
            pass


@pytest.mark.parametrize("key", [s["key"] for s in sims.SIMULATIONS])
def test_simulation_passes(client, key):
    r = client.post(f"/api/simulations/{key}/run", headers=H)
    assert r.status_code == 200, r.text
    res = r.json()
    failed = [(st["label"], c) for st in res["steps"] for c in st["checks"] if not c["ok"]]
    errors = [st["error"] for st in res["steps"] if st["error"]]
    assert res["ok"], f"{key}: {failed} {errors}"


def test_catalogue_lists_steps(client):
    cat = client.get("/api/simulations", headers=H).json()
    assert len(cat) == len(sims.SIMULATIONS) and all(c["steps"] for c in cat)

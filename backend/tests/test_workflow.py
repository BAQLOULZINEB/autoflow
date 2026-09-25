"""End-to-end scenario tests (docs/06-demo-plan). Run: pytest -q"""
import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_autoflow.db"
os.environ["CHECKPOINT_DB"] = "./test_ckpt.db"
os.environ["LLM_PROVIDER"] = "none"

import pytest
from fastapi.testclient import TestClient

from app import clock
from app.db import Request, session
from app.main import app
from app.workflow import orchestrator as o

H = {"X-Admin-Token": "change-me-admin"}


@pytest.fixture(scope="module")
def client():
    o.reset_and_seed()
    with TestClient(app) as c:
        yield c
    # SQLite files stay locked on Windows until the engine is disposed
    from app.db import get_engine
    from app.workflow.graph import get_graph
    get_engine().dispose()
    get_graph.cache_clear()
    import gc; gc.collect()
    for f in ("test_autoflow.db", "test_ckpt.db"):
        try:
            Path(f).unlink(missing_ok=True)
        except PermissionError:
            pass


def _load(client, key):
    r = client.post(f"/api/demo/load/{key}", headers=H)
    assert r.status_code == 200, r.text
    return r.json()


def test_auth_required(client):
    assert client.get("/api/requests").status_code == 401


A_ID = {}


def test_scenario_a_standard_quote(client):
    d = _load(client, "A")
    A_ID["id"] = d["id"]
    assert d["state"] == "quote_ready"
    assert d["structured"]["intent"] == "quote"
    assert d["structured"]["pickup_date"] == "2026-10-12" and d["structured"]["return_date"] == "2026-10-15"
    assert d["availability"]["status"] == "available"
    assert d["availability"]["options"][0]["vehicle_id"] == "CIT-03"
    assert "230 MAD" in d["followup"]["draft_fr"]
    assert d["pending_interrupt"] is not None
    # staff approves → sent → pending_customer with reminder scheduled
    r = client.post(f"/api/requests/{d['id']}/decision", headers=H, json={"action": "approve", "actor": "staff:Salma"}).json()
    assert r["state"] == "pending_customer"
    assert r["follow_ups"][0]["status"] == "scheduled"


def test_scenario_b_alternative(client):
    d = _load(client, "B")
    a = d["availability"]
    assert a["status"] == "alternative"
    ids = [x["vehicle_id"] for x in a["alternatives"]]
    assert "BER-02" in ids
    assert any("maintenance" in r for r in a["reasons"])
    assert d["followup"]["draft_kind"] == "alternative"


def test_scenario_c_ambiguous_sensitive(client):
    d = _load(client, "C")
    assert d["state"] == "needs_human"
    assert d["review_level"] == "manager"
    assert "ambiguous_dates" in d["structured"]["flags"]
    assert "discount_requested" in d["structured"]["flags"]
    assert d["drafts"][0]["kind"] == "clarification"
    # manager completes the fields → availability re-run → still sensitive (discount) → escalated
    r = client.post(f"/api/requests/{d['id']}/decision", headers=H, json={
        "action": "complete", "actor": "manager:Omar",
        "fields": {"pickup_date": "2026-10-24", "return_date": "2026-10-26", "vehicle_category": "citadine"}}).json()
    assert r["state"] == "escalated"
    assert r["availability"]["status"] == "available"
    r = client.post(f"/api/requests/{d['id']}/decision", headers=H,
                    json={"action": "approve", "actor": "manager:Omar", "note": "remise 10% accordée"}).json()
    assert r["state"] == "pending_customer"


def test_scenario_d_complaint(client):
    d = _load(client, "D")
    assert d["state"] == "escalated" and d["priority"] == "high"
    assert d["drafts"] == []


def test_follow_up_engine_time_travel(client):
    rid = A_ID["id"]
    client.post("/api/demo/advance", headers=H, json={"hours": 25})
    d = client.get(f"/api/requests/{rid}", headers=H).json()
    assert d["review_reason"].startswith("Relance n°1")
    assert d["drafts"][-1]["kind"] == "reminder"
    r = client.post(f"/api/requests/{rid}/decision", headers=H, json={"action": "send_reminder", "actor": "staff:Salma"}).json()
    assert r["state"] == "pending_customer"
    client.post("/api/demo/advance", headers=H, json={"hours": 80})
    d = client.get(f"/api/requests/{rid}", headers=H).json()
    assert d["state"] == "needs_human"
    assert any(e["to"] == "stalled" for e in d["events"])


def test_customer_accepts_creates_booking(client):
    d = _load(client, "E")
    client.post(f"/api/requests/{d['id']}/decision", headers=H, json={"action": "approve", "actor": "staff:Salma"})
    r = client.post(f"/api/requests/{d['id']}/customer-reply", headers=H, json={"accepted": True}).json()
    assert r["state"] == "confirmed"
    fleet = client.get("/api/fleet", headers=H).json()
    assert any(b["request_id"] == d["id"] for b in fleet["bookings"])


def test_kpis_and_graph(client):
    k = client.get("/api/kpis", headers=H).json()
    assert k["total_requests"] >= 5 and k["human_handoffs"] >= 3
    g = client.get("/api/graph", headers=H).json()["mermaid"]
    assert "human_review" in g and "availability" in g

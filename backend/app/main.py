"""AutoFlow API — FastAPI façade over the LangGraph orchestrator.

Auth: every /api/* route except /api/health and /api/public/* requires the
header `X-Admin-Token` (single shared token for the pilot; roles are carried
in the `actor` field of each decision, e.g. "staff:Salma" / "manager:Omar").
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select

from . import clock
from . import analytics as bi
from .config import DATA_DIR, get_settings
from .db import Booking, Customer, Draft, Event, FollowUp, Request, Review, Setting, Vehicle, init_db, session
from .excel_import import import_workbook
from .rules import load_rules
from . import simulations as sims
from .official_images import cached_vehicle_image, local_vehicle_image, resolve_official_image
from .workflow import orchestrator as orch
from .workflow.explain import explain
from .workflow.graph import get_graph
from .workflow.store import IllegalTransition

settings = get_settings()
image_warmer = ThreadPoolExecutor(max_workers=3, thread_name_prefix="vehicle-image-cache")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if settings.seed_demo:
        # A Vercel function starts from an empty /tmp SQLite database after a
        # cold start. The workflow seed creates the operational tables, while
        # the workbook seed creates the BI tables (locations, expenses and
        # appointments). Keeping both together prevents a half-seeded UI where
        # Fleet works but dashboard/garage endpoints raise "no such table".
        with session() as db:
            workflow_seeded = db.get(Setting, "seeded_at") is not None
            workbook_seeded = db.get(Setting, "excel_imported_at") is not None
        if not workflow_seeded:
            orch.reset_and_seed()
        if settings.auto_seed_workbook and not workbook_seeded:
            workbook = DATA_DIR / "autoflow_agence.xlsx"
            if not workbook.exists():
                raise RuntimeError(f"Demo workbook is missing: {workbook}")
            result = import_workbook(workbook.read_bytes())
            if not result.ok:
                raise RuntimeError(f"Demo workbook seed failed: {result.errors}")
    yield


app = FastAPI(title="AutoFlow API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_list or ["*"], allow_credentials=False,
                   allow_methods=["*"], allow_headers=["*"])


def auth(x_admin_token: str | None = Header(default=None)):
    if x_admin_token != settings.admin_token:
        raise HTTPException(401, "Token administrateur invalide.")


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #
class IntakeIn(BaseModel):
    message: str = Field(min_length=3, max_length=2000)
    channel: str = "whatsapp"
    customer_name: str = ""


class DecisionIn(BaseModel):
    action: str  # approve | edit | reject | close | complete | send_reminder | call_done
    actor: str = "staff"
    body: str | None = None
    note: str = ""
    fields: dict = Field(default_factory=dict)


class CustomerReplyIn(BaseModel):
    accepted: bool
    actor: str = "staff"


class AdvanceIn(BaseModel):
    hours: float = 24


class LoginIn(BaseModel):
    token: str


# --------------------------------------------------------------------------- #
# Public
# --------------------------------------------------------------------------- #
@app.get("/api/health")
def health():
    return {"ok": True, "llm": settings.llm_provider, "version": "0.1.0", "clock": clock.now().isoformat(timespec="seconds")}


@app.post("/api/public/intake")
def public_intake(body: IntakeIn):
    """Customer-facing form / n8n webhook target. No token: it only creates a request."""
    rid = orch.submit(body.message, body.channel, body.customer_name)
    return {"request_id": rid, "message": "Merci ! Votre demande a été reçue, l'agence revient vers vous rapidement."}


@app.post("/api/auth/login")
def login(body: LoginIn):
    if body.token != settings.admin_token:
        raise HTTPException(401, "Token invalide.")
    return {"ok": True}


# --------------------------------------------------------------------------- #
# Requests
# --------------------------------------------------------------------------- #
def _req_dict(r: Request) -> dict:
    return {"id": r.id, "customer_name": r.customer_name, "customer_id": r.customer_id, "channel": r.channel,
            "raw_message": r.raw_message, "received_at": r.received_at.isoformat(timespec="seconds"),
            "state": r.state, "intent": r.intent, "structured": r.structured, "availability": r.availability,
            "followup": r.followup, "review_reason": r.review_reason, "review_level": r.review_level,
            "priority": r.priority, "hops": r.hops, "updated_at": r.updated_at.isoformat(timespec="seconds")}


@app.post("/api/requests", dependencies=[Depends(auth)])
def create_request(body: IntakeIn):
    rid = orch.submit(body.message, body.channel, body.customer_name)
    return get_request(rid)


@app.get("/api/requests", dependencies=[Depends(auth)])
def list_requests(state: str | None = None, limit: int = 100):
    orch.sweep()
    with session() as db:
        q = select(Request).order_by(Request.received_at.desc()).limit(limit)
        if state:
            q = q.where(Request.state == state)
        return [_req_dict(r) for r in db.scalars(q)]


@app.get("/api/requests/{rid}", dependencies=[Depends(auth)])
def get_request(rid: str):
    with session() as db:
        r = db.get(Request, rid)
        if not r:
            raise HTTPException(404, "Demande introuvable.")
        out = _req_dict(r)
        out["drafts"] = [{"id": d.id, "kind": d.kind, "body_fr": d.body_fr, "generated_at": d.generated_at.isoformat(timespec="seconds"),
                          "edited": d.edited, "sent_by": d.sent_by, "sent_at": d.sent_at.isoformat(timespec="seconds") if d.sent_at else None}
                         for d in db.query(Draft).filter_by(request_id=rid).order_by(Draft.id)]
        out["events"] = [{"id": e.id, "from": e.from_state, "to": e.to_state, "actor": e.actor, "reason": e.reason,
                          "ts": e.ts.isoformat(timespec="seconds")} for e in db.query(Event).filter_by(request_id=rid).order_by(Event.id)]
        out["reviews"] = [{"id": v.id, "reason": v.reason, "level": v.level, "priority": v.priority, "decision": v.decision,
                           "actor": v.actor, "note": v.note, "opened_at": v.opened_at.isoformat(timespec="seconds"),
                           "closed_at": v.closed_at.isoformat(timespec="seconds") if v.closed_at else None}
                          for v in db.query(Review).filter_by(request_id=rid).order_by(Review.id)]
        out["follow_ups"] = [{"id": f.id, "due_at": f.due_at.isoformat(timespec="seconds"), "reminder_no": f.reminder_no,
                              "status": f.status, "outcome": f.outcome} for f in db.query(FollowUp).filter_by(request_id=rid).order_by(FollowUp.id)]
    out["pending_interrupt"] = orch.pending_interrupt(rid)
    return out


@app.get("/api/requests/{rid}/trace", dependencies=[Depends(auth)])
def trace(rid: str):
    """Decision trace: graph path + every rule evaluated, for the 'Suivi en direct' panel."""
    with session() as db:
        if not db.get(Request, rid):
            raise HTTPException(404, "Demande introuvable.")
    return explain(rid, orch.pending_interrupt(rid))


@app.get("/api/live", dependencies=[Depends(auth)])
def live(since: int = 0, limit: int = 30):
    """Live feed: events newer than `since` (event id) + queue size. Polled by the dashboard."""
    orch.sweep()
    with session() as db:
        q = db.query(Event).filter(Event.id > since).order_by(Event.id.desc()).limit(limit)
        evs = [{"id": e.id, "request_id": e.request_id, "from": e.from_state, "to": e.to_state, "actor": e.actor,
                "reason": e.reason, "ts": e.ts.isoformat(timespec="seconds")} for e in q]
        open_reviews = db.query(Review).filter(Review.closed_at.is_(None)).count()
        last = db.query(Event.id).order_by(Event.id.desc()).first()
    return {"events": evs, "last_id": last[0] if last else 0, "open_reviews": open_reviews,
            "clock": clock.now().isoformat(timespec="seconds")}


@app.post("/api/requests/{rid}/decision", dependencies=[Depends(auth)])
def decide(rid: str, body: DecisionIn):
    with session() as db:
        r = db.get(Request, rid)
        if not r:
            raise HTTPException(404, "Demande introuvable.")
        state = r.state
    try:
        if body.action == "send_reminder":
            orch.send_reminder(rid, body.actor, body.body)
        elif body.action in ("call_done",) or (state in ("needs_human", "stalled") and orch.pending_interrupt(rid) is None):
            orch.staff_action_on_stalled(rid, body.action if body.action in ("close", "call_done") else "close", body.actor, body.note)
        else:
            orch.resume(rid, body.model_dump())
    except (ValueError, IllegalTransition) as exc:
        raise HTTPException(409, str(exc))
    return get_request(rid)


@app.post("/api/requests/{rid}/customer-reply", dependencies=[Depends(auth)])
def customer_reply(rid: str, body: CustomerReplyIn):
    try:
        orch.customer_replied(rid, body.accepted, body.actor)
    except IllegalTransition as exc:
        raise HTTPException(409, str(exc))
    return get_request(rid)


# --------------------------------------------------------------------------- #
# Queue / data / KPIs
# --------------------------------------------------------------------------- #
@app.get("/api/reviews", dependencies=[Depends(auth)])
def open_reviews():
    orch.sweep()
    with session() as db:
        rows = db.query(Review, Request).join(Request, Request.id == Review.request_id).filter(Review.closed_at.is_(None)) \
            .order_by(Review.priority.desc(), Review.opened_at.asc()).all()
        return [{"review_id": v.id, "request_id": r.id, "customer_name": r.customer_name, "channel": r.channel, "state": r.state,
                 "level": v.level, "priority": v.priority, "reason": v.reason,
                 "opened_at": v.opened_at.isoformat(timespec="seconds"), "intent": r.intent,
                 "draft_kind": (r.followup or {}).get("draft_kind"), "action": (r.followup or {}).get("action")}
                for v, r in rows]


@app.get("/api/fleet", dependencies=[Depends(auth)])
def fleet():
    with session() as db:
        vs = [{"id": v.id, "plate": v.plate, "category": v.category, "model": v.model, "transmission": v.transmission, "location": v.location,
               "status": v.status, "maintenance_until": v.maintenance_until, "daily_rate_mad": v.daily_rate_mad}
              for v in db.query(Vehicle).order_by(Vehicle.id)]
        bs = [{"id": b.id, "vehicle_id": b.vehicle_id, "request_id": b.request_id, "start_date": b.start_date,
               "end_date": b.end_date, "status": b.status} for b in db.query(Booking).order_by(Booking.start_date)]
        cs = [{"id": c.id, "name": c.name, "phone_masked": c.phone_masked, "is_vip": c.is_vip, "notes": c.notes}
              for c in db.query(Customer)]
    return {"vehicles": vs, "bookings": bs, "customers": cs}


@app.get("/api/rules", dependencies=[Depends(auth)])
def rules():
    return load_rules()


@app.get("/api/kpis", dependencies=[Depends(auth)])
def kpis():
    orch.sweep()
    return orch.kpis()


@app.get("/api/events", dependencies=[Depends(auth)])
def events(limit: int = 50):
    with session() as db:
        return [{"id": e.id, "request_id": e.request_id, "from": e.from_state, "to": e.to_state, "actor": e.actor,
                 "reason": e.reason, "ts": e.ts.isoformat(timespec="seconds")}
                for e in db.query(Event).order_by(Event.id.desc()).limit(limit)]


@app.get("/api/graph", dependencies=[Depends(auth)])
def graph_mermaid():
    return {"mermaid": get_graph().get_graph().draw_mermaid()}


# --------------------------------------------------------------------------- #
# Simulations (scripted business cases = demo + acceptance tests)
# --------------------------------------------------------------------------- #
@app.get("/api/simulations", dependencies=[Depends(auth)])
def list_simulations():
    return sims.catalogue()


@app.post("/api/simulations/{key}/run", dependencies=[Depends(auth)])
def run_simulation(key: str):
    try:
        return sims.run(key)
    except KeyError:
        raise HTTPException(404, "Simulation inconnue.")


@app.post("/api/simulations/run-all", dependencies=[Depends(auth)])
def run_all_simulations():
    results = [sims.run(s["key"]) for s in sims.SIMULATIONS]
    return {"ok": all(r["ok"] for r in results), "results": results}


# --------------------------------------------------------------------------- #
# Demo controls
# --------------------------------------------------------------------------- #
@app.get("/api/demo/scenarios", dependencies=[Depends(auth)])
def scenarios():
    return orch.scenarios()


@app.post("/api/demo/load/{key}", dependencies=[Depends(auth)])
def load_scenario(key: str):
    for sc in orch.scenarios():
        if sc["key"].upper() == key.upper():
            rid = orch.submit(sc["message"], sc["channel"], sc["customer"])
            return get_request(rid)
    raise HTTPException(404, "Scénario inconnu.")


@app.post("/api/demo/reset", dependencies=[Depends(auth)])
def reset(history: bool = True):
    """history=true replays 6 weeks of fictional activity; false = empty agency."""
    orch.reset_and_seed(with_history=history)
    return {"ok": True, "history": history}


@app.post("/api/demo/advance", dependencies=[Depends(auth)])
def advance(body: AdvanceIn):
    clock.advance(body.hours)
    return {"clock": clock.now().isoformat(timespec="seconds"), "sweep": orch.sweep()}


@app.post("/api/demo/sweep", dependencies=[Depends(auth)])
def sweep():
    return orch.sweep()


# --------------------------------------------------------------------------- #
# Analytics & BI endpoints (AutoFlow Pro)
# --------------------------------------------------------------------------- #
@app.get("/api/bi/dashboard", dependencies=[Depends(auth)])
def bi_dashboard():
    return bi.dashboard_kpis()


@app.get("/api/bi/revenue/daily", dependencies=[Depends(auth)])
def bi_revenue_daily(month: int = 9, year: int = 2026):
    return bi.revenue_by_day(month, year)


@app.get("/api/bi/revenue/monthly", dependencies=[Depends(auth)])
def bi_revenue_monthly():
    return bi.revenue_by_month()


@app.get("/api/bi/revenue/category", dependencies=[Depends(auth)])
def bi_revenue_by_cat(month: int | None = None, year: int = 2026):
    return bi.revenue_by_category(month, year)


@app.get("/api/bi/expenses/category", dependencies=[Depends(auth)])
def bi_expenses_cat(month: int | None = None, year: int = 2026):
    return bi.expenses_by_category(month, year)


@app.get("/api/bi/expenses/vehicle", dependencies=[Depends(auth)])
def bi_expenses_vehicle(month: int | None = None, year: int = 2026):
    return bi.expenses_by_vehicle(month, year)


@app.get("/api/bi/fleet/categories", dependencies=[Depends(auth)])
def bi_fleet_cats():
    return bi.fleet_category_breakdown()


@app.get("/api/bi/fleet/occupancy", dependencies=[Depends(auth)])
def bi_fleet_occupancy(month: int | None = None, year: int = 2026):
    return bi.occupancy_by_vehicle(month, year)


@app.get("/api/bi/fleet/garage", dependencies=[Depends(auth)])
def bi_fleet_garage(month: int | None = None, year: int = 2026):
    return bi.garage_overview(month, year)


@app.get("/api/media/vehicle-image", dependencies=[Depends(auth)])
def official_vehicle_image(model: str):
    """Return the commercial image published by the official model page."""
    return resolve_official_image(model.strip())


@app.get("/api/media/vehicle-image/file")
def approved_vehicle_image_file(model: str):
    """Serve one of the fixed, user-approved local photos for Garage."""
    image = local_vehicle_image(model.strip()) or cached_vehicle_image(model.strip())
    if image is None:
        raise HTTPException(404, "Visuel véhicule introuvable.")
    media_type = {
        ".png": "image/png", ".webp": "image/webp", ".avif": "image/avif",
    }.get(image.suffix.lower(), "image/jpeg")
    return FileResponse(image, media_type=media_type)


@app.post("/api/media/vehicle-images/warm", dependencies=[Depends(auth)])
def warm_vehicle_images():
    """Populate the local Garage image cache without delaying the UI."""
    with session() as db:
        models = sorted({model for model in db.scalars(select(Vehicle.model)).all() if model})
    image_warmer.submit(lambda: [resolve_official_image(model) for model in models])
    return {"queued": len(models)}


@app.get("/api/bi/appointments", dependencies=[Depends(auth)])
def bi_appointments(days: int = 14):
    return bi.upcoming_appointments(days=days)


@app.get("/api/bi/clients/top", dependencies=[Depends(auth)])
def bi_top_clients(limit: int = 20):
    return bi.client_ranking(limit)


@app.get("/api/bi/locations", dependencies=[Depends(auth)])
def bi_locations(month: int | None = None, year: int = 2026, limit: int = 200):
    from .analytics import Location as Loc
    from sqlalchemy import extract as ex
    with session() as db:
        q = db.query(Loc)
        if month:
            q = q.filter(ex("month", Loc.date_out) == month, ex("year", Loc.date_out) == year)
        q = q.order_by(Loc.date_out.desc()).limit(limit)
        return [{"id": l.id, "plate": l.plate, "cin": l.cin, "price_per_day": l.price_per_day,
                 "date_out": l.date_out.isoformat(), "date_in": l.date_in.isoformat(),
                 "days": l.days, "amount": l.amount, "channel": l.channel, "status": l.status}
                for l in q.all()]


@app.get("/api/bi/expenses", dependencies=[Depends(auth)])
def bi_expenses_list(month: int | None = None, year: int = 2026, limit: int = 200):
    from .analytics import Expense as Exp
    from sqlalchemy import extract as ex
    with session() as db:
        q = db.query(Exp)
        if month:
            q = q.filter(ex("month", Exp.date) == month, ex("year", Exp.date) == year)
        q = q.order_by(Exp.date.desc()).limit(limit)
        return [{"id": e.id, "date": e.date.isoformat(), "plate": e.plate, "category": e.category,
                 "amount": e.amount, "supplier": e.supplier, "note": e.note}
                for e in q.all()]


@app.get("/api/bi/appointments/list", dependencies=[Depends(auth)])
def bi_appointments_list(days: int = 30):
    return bi.upcoming_appointments(days=days)


# --------------------------------------------------------------------------- #
# Excel import
# --------------------------------------------------------------------------- #
@app.post("/api/excel/import", dependencies=[Depends(auth)])
async def excel_import(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(400, "Seuls les fichiers .xlsx sont acceptés.")
    data = await file.read()
    if len(data) > 50 * 1024 * 1024:
        raise HTTPException(400, "Fichier trop volumineux (max 50 Mo).")
    result = import_workbook(data)
    return result.dict()


@app.post("/api/excel/seed", dependencies=[Depends(auth)])
def excel_seed():
    """Load the generated demo workbook."""
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "data" / "autoflow_agence.xlsx"
    if not p.exists():
        raise HTTPException(404, "Fichier de démonstration introuvable. Lancez generate_workbook.py.")
    result = import_workbook(p.read_bytes())
    return result.dict()

"""Analytics models & queries — the BI layer for AutoFlow Pro.

Tables: Location (rental history), Expense, Appointment.
All KPIs are computed live from these tables (never stored).
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from sqlalchemy import (Boolean, Date, Float, Integer, String, Text,
                        create_engine, func, extract, case, literal)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .db import session, Vehicle


class AnalyticsBase(DeclarativeBase):
    pass


class Location(AnalyticsBase):
    __tablename__ = "locations"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    plate: Mapped[str] = mapped_column(String, index=True)
    cin: Mapped[str] = mapped_column(String, index=True)
    price_per_day: Mapped[int] = mapped_column(Integer, default=0)
    date_out: Mapped[date] = mapped_column(Date)
    date_in: Mapped[date] = mapped_column(Date)
    days: Mapped[int] = mapped_column(Integer, default=1)
    amount: Mapped[int] = mapped_column(Integer, default=0)
    channel: Mapped[str] = mapped_column(String, default="Comptoir")
    status: Mapped[str] = mapped_column(String, default="terminee")


class Expense(AnalyticsBase):
    __tablename__ = "expenses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date)
    plate: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    category: Mapped[str] = mapped_column(String)
    amount: Mapped[int] = mapped_column(Integer)
    supplier: Mapped[str] = mapped_column(String, default="")
    note: Mapped[str] = mapped_column(Text, default="")


class Appointment(AnalyticsBase):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    time: Mapped[str] = mapped_column(String, default="09:00")
    type: Mapped[str] = mapped_column(String)
    plate: Mapped[str | None] = mapped_column(String, nullable=True)
    cin: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="prévu")
    note: Mapped[str] = mapped_column(Text, default="")


# --------------------------------------------------------------------------- #
# KPI computations
# --------------------------------------------------------------------------- #
def dashboard_kpis(today: date | None = None) -> dict:
    """All the numbers the dashboard needs, computed live."""
    today = today or date.today()
    month_start = today.replace(day=1)
    prev_month_start = (month_start - timedelta(days=1)).replace(day=1)

    with session() as db:
        # Revenue
        rev_month = db.query(func.coalesce(func.sum(Location.amount), 0)).filter(
            Location.date_out >= month_start, Location.date_out <= today).scalar()
        rev_prev = db.query(func.coalesce(func.sum(Location.amount), 0)).filter(
            Location.date_out >= prev_month_start, Location.date_out < month_start).scalar()

        # Active rentals right now
        active = db.query(func.count()).filter(
            Location.date_out <= today, Location.date_in > today, Location.status != "terminee").scalar()

        # Total rentals this month
        rentals_month = db.query(func.count()).filter(
            Location.date_out >= month_start, Location.date_out <= today).scalar()
        rentals_prev = db.query(func.count()).filter(
            Location.date_out >= prev_month_start, Location.date_out < month_start).scalar()

        # Fleet stats
        total_vehicles = db.query(func.count()).select_from(Vehicle).scalar()
        in_maintenance = db.query(func.count()).select_from(Vehicle).filter(Vehicle.status == "maintenance").scalar()

        # Occupancy rate (% of fleet rented today)
        rented_today = db.query(func.count(func.distinct(Location.plate))).filter(
            Location.date_out <= today, Location.date_in > today).scalar()
        occupancy = round(rented_today / total_vehicles * 100, 1) if total_vehicles else 0

        # Expenses this month
        exp_month = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.date >= month_start, Expense.date <= today).scalar()
        exp_prev = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.date >= prev_month_start, Expense.date < month_start).scalar()

        # Avg rental duration
        avg_days = db.query(func.avg(Location.days)).filter(
            Location.date_out >= month_start).scalar()

        # Avg daily rate
        avg_rate = db.query(func.avg(Location.price_per_day)).filter(
            Location.date_out >= month_start).scalar()

        # Appointments today & upcoming
        appts_today = db.query(func.count()).select_from(Appointment).filter(
            Appointment.date == today).scalar()
        appts_upcoming = db.query(func.count()).select_from(Appointment).filter(
            Appointment.date > today, Appointment.date <= today + timedelta(days=7)).scalar()

        # Top channels
        channels = db.query(Location.channel, func.count()).filter(
            Location.date_out >= month_start).group_by(Location.channel).order_by(func.count().desc()).all()

        # Unique clients this month
        clients_month = db.query(func.count(func.distinct(Location.cin))).filter(
            Location.date_out >= month_start).scalar()

    return {
        "revenue_month": rev_month,
        "revenue_prev_month": rev_prev,
        "revenue_delta_pct": round((rev_month - rev_prev) / rev_prev * 100, 1) if rev_prev else None,
        "active_rentals": active,
        "rentals_month": rentals_month,
        "rentals_prev_month": rentals_prev,
        "total_vehicles": total_vehicles,
        "in_maintenance": in_maintenance,
        "occupancy_pct": occupancy,
        "rented_today": rented_today,
        "expenses_month": exp_month,
        "expenses_prev_month": exp_prev,
        "profit_month": rev_month - exp_month,
        "avg_rental_days": round(avg_days, 1) if avg_days else None,
        "avg_daily_rate": round(avg_rate) if avg_rate else None,
        "appointments_today": appts_today,
        "appointments_week": appts_upcoming,
        "channels": [{"name": c, "count": n} for c, n in channels],
        "clients_month": clients_month,
        "today": today.isoformat(),
    }


def revenue_by_day(month: int, year: int = 2026) -> list[dict]:
    """Daily revenue for a given month — for the area chart."""
    with session() as db:
        rows = db.query(
            Location.date_out,
            func.sum(Location.amount),
            func.count()
        ).filter(
            extract("month", Location.date_out) == month,
            extract("year", Location.date_out) == year,
        ).group_by(Location.date_out).order_by(Location.date_out).all()
    return [{"date": d.isoformat(), "revenue": r, "count": c} for d, r, c in rows]


def revenue_by_month() -> list[dict]:
    """Monthly revenue — for the bar chart."""
    with session() as db:
        rows = db.query(
            extract("year", Location.date_out).label("y"),
            extract("month", Location.date_out).label("m"),
            func.sum(Location.amount),
            func.count()
        ).group_by("y", "m").order_by("y", "m").all()
    months_fr = {1: "Jan", 2: "Fév", 3: "Mar", 4: "Avr", 5: "Mai", 6: "Juin",
                 7: "Juil", 8: "Août", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Déc"}
    return [{"month": f"{months_fr.get(int(m), m)} {int(y)}", "revenue": r, "count": c}
            for y, m, r, c in rows]


def expenses_by_category(month: int | None = None, year: int = 2026) -> list[dict]:
    """Expenses grouped by category — for the donut chart."""
    with session() as db:
        q = db.query(Expense.category, func.sum(Expense.amount)).group_by(Expense.category)
        if month:
            q = q.filter(extract("month", Expense.date) == month, extract("year", Expense.date) == year)
        rows = q.order_by(func.sum(Expense.amount).desc()).all()
    return [{"category": c, "amount": a} for c, a in rows]


def expenses_by_vehicle(month: int | None = None, year: int = 2026) -> list[dict]:
    """Total expenses per vehicle — for the horizontal bar chart."""
    with session() as db:
        q = db.query(Expense.plate, func.sum(Expense.amount)).filter(Expense.plate.isnot(None), Expense.plate != "")
        if month:
            q = q.filter(extract("month", Expense.date) == month, extract("year", Expense.date) == year)
        rows = q.group_by(Expense.plate).order_by(func.sum(Expense.amount).desc()).limit(15).all()
    return [{"plate": p, "amount": a} for p, a in rows]


def fleet_category_breakdown() -> list[dict]:
    """Vehicle count by category — for the pie chart."""
    with session() as db:
        rows = db.query(Vehicle.category, func.count()).group_by(Vehicle.category).order_by(func.count().desc()).all()
    return [{"category": c, "count": n} for c, n in rows]


def occupancy_by_vehicle(month: int | None = None, year: int = 2026) -> list[dict]:
    """Occupancy rate per vehicle — for the heatmap / bar."""
    today = date.today()
    with session() as db:
        vehicles = db.query(Vehicle).all()
    results = []
    for v in vehicles:
        with session() as db:
            q = db.query(func.coalesce(func.sum(Location.days), 0)).filter(Location.plate == v.id)
            if month:
                q = q.filter(extract("month", Location.date_out) == month, extract("year", Location.date_out) == year)
            rented_days = q.scalar()
        days_in_month = 30 if month else (today - date(year, 7, 1)).days
        rate = round(rented_days / max(1, days_in_month) * 100, 1)
        results.append({"vehicle_id": v.id, "model": v.model, "category": v.category,
                        "rented_days": rented_days, "occupancy_pct": min(100, rate)})
    results.sort(key=lambda x: -x["occupancy_pct"])
    return results


def upcoming_appointments(today: date | None = None, days: int = 14) -> list[dict]:
    """Appointments in the next N days."""
    today = today or date.today()
    with session() as db:
        rows = db.query(Appointment).filter(
            Appointment.date >= today, Appointment.date <= today + timedelta(days=days)
        ).order_by(Appointment.date, Appointment.time).all()
    return [{"id": a.id, "date": a.date.isoformat(), "time": a.time, "type": a.type,
             "plate": a.plate, "cin": a.cin, "status": a.status, "note": a.note} for a in rows]


def revenue_by_category(month: int | None = None, year: int = 2026) -> list[dict]:
    """Revenue by vehicle category — for the stacked bar.
    Needs a plate→category mapping since Location stores plates, Vehicle stores codes."""
    # Build plate→category from locations + fleet data
    with session() as db:
        # Get all locations
        q = db.query(Location)
        if month:
            q = q.filter(extract("month", Location.date_out) == month, extract("year", Location.date_out) == year)
        locs = q.all()
        # Get plate→category from the workbook generator's mapping stored alongside
        # Since we store code in Vehicle and plate in Location, we need the mapping
        # For now, aggregate by price range as proxy for category
        cats = {"< 250": 0, "250–400": 0, "400–600": 0, "600–900": 0, "> 900": 0}
        cat_count = {"< 250": 0, "250–400": 0, "400–600": 0, "600–900": 0, "> 900": 0}
        cat_labels = {
            "< 250": "Économique", "250–400": "Compacte / Berline",
            "400–600": "SUV", "600–900": "Premium / 4x4", "> 900": "Luxe"
        }
        for l in locs:
            p = l.price_per_day
            if p < 250:
                k = "< 250"
            elif p < 400:
                k = "250–400"
            elif p < 600:
                k = "400–600"
            elif p < 900:
                k = "600–900"
            else:
                k = "> 900"
            cats[k] += l.amount
            cat_count[k] += 1
    return [{"category": cat_labels[k], "revenue": cats[k], "count": cat_count[k]}
            for k in cats if cats[k] > 0]


def client_ranking(limit: int = 20) -> list[dict]:
    """Top clients by total spend."""
    with session() as db:
        rows = db.query(
            Location.cin, func.sum(Location.amount), func.count()
        ).group_by(Location.cin).order_by(func.sum(Location.amount).desc()).limit(limit).all()
    return [{"cin": c, "total": t, "rentals": n} for c, t, n in rows]

"""Generate the agency's Excel workbook — realistic Rabat car-rental data.

Based on **real 2025-2026 Moroccan market prices** from RAKB, OneClickDrive,
Avito, GoRide, CasaRide, MyMobiRent and agency websites. Prices are in MAD.
Plate format: 5-digit number + Arabic letter (transliterated A/B/D/H/W) + region 1.

Period: **July – September 2026** (3 months, haute saison / rentrée).
Seeded (2026) so every demo is reproducible.

Run from backend/:  python data/generate_workbook.py
"""
from __future__ import annotations

import csv
import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

rng = random.Random(2026)
TODAY = date(2026, 9, 25)
START = date(2026, 7, 1)
END   = date(2026, 9, 30)
OUT   = HERE / "autoflow_agence.xlsx"

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FLEET — real models sold / rented in Morocco, real MAD market prices  ║
# ╚══════════════════════════════════════════════════════════════════════════╝
# Sources (2025-2026): rakb.ma, oneclickdrive.ma, avito.ma, goride.ma,
#   casaride.ma, mymobirent.com, banyolti.com, rayhane-cars.net
# id, model, category, transmission, base_rate MAD/day, location, status, maint_until
FLEET_SPEC = [
    # ── Économiques / Citadines (150–280 MAD) ─────────────────────────────
    ("CIT-01", "Dacia Sandero",          "citadine",    "manuelle",     200, "Agdal",              "active", None),
    ("CIT-02", "Dacia Sandero Stepway",  "citadine",    "manuelle",     230, "Hay Riad",           "active", None),
    ("CIT-03", "Renault Clio 5",         "citadine",    "manuelle",     250, "Agdal",              "active", None),
    ("CIT-04", "Renault Clio 5",         "citadine",    "automatique",  280, "Aéroport Rabat-Salé","active", None),
    ("CIT-05", "Hyundai i10",            "citadine",    "manuelle",     180, "Agdal",              "active", None),
    ("CIT-06", "Hyundai i20",            "citadine",    "manuelle",     220, "Hay Riad",           "active", None),
    ("CIT-07", "Peugeot 208",            "citadine",    "manuelle",     260, "Agdal",              "active", None),
    ("CIT-08", "Peugeot 208",            "citadine",    "automatique",  300, "Aéroport Rabat-Salé","active", None),
    ("CIT-09", "Fiat 500",               "citadine",    "manuelle",     250, "Hay Riad",           "active", None),
    ("CIT-10", "Kia Picanto",            "citadine",    "manuelle",     190, "Agdal",              "active", None),
    ("CIT-11", "Toyota Yaris",           "citadine",    "automatique",  290, "Hay Riad",           "active", None),
    ("CIT-12", "Volkswagen Polo",        "citadine",    "manuelle",     270, "Aéroport Rabat-Salé","active", None),
    # ── Compactes / Berlines (280–500 MAD) ────────────────────────────────
    ("BER-01", "Dacia Logan",            "berline",     "manuelle",     180, "Agdal",              "active", None),
    ("BER-02", "Renault Mégane",         "berline",     "automatique",  380, "Hay Riad",           "active", None),
    ("BER-03", "Peugeot 308",            "berline",     "automatique",  400, "Agdal",              "active", None),
    ("BER-04", "Hyundai Accent",         "berline",     "automatique",  350, "Hay Riad",           "active", None),
    ("BER-05", "Toyota Corolla",         "berline",     "automatique",  420, "Agdal",              "active", None),
    ("BER-06", "Skoda Octavia",          "berline",     "automatique",  450, "Aéroport Rabat-Salé","active", None),
    ("BER-07", "Fiat Tipo",              "berline",     "manuelle",     280, "Agdal",              "active", None),
    ("BER-08", "Volkswagen Jetta",       "berline",     "automatique",  480, "Hay Riad",           "active", None),
    # ── SUV / Crossover (400–700 MAD) ─────────────────────────────────────
    ("SUV-01", "Dacia Duster",           "suv",         "manuelle",     400, "Agdal",              "active", None),
    ("SUV-02", "Dacia Duster",           "suv",         "automatique",  450, "Hay Riad",           "active", None),
    ("SUV-03", "Hyundai Tucson",         "suv",         "automatique",  550, "Agdal",              "active", None),
    ("SUV-04", "Hyundai Creta",          "suv",         "automatique",  500, "Hay Riad",           "active", None),
    ("SUV-05", "Kia Sportage",           "suv",         "automatique",  600, "Agdal",              "active", None),
    ("SUV-06", "Peugeot 3008",           "suv",         "automatique",  650, "Aéroport Rabat-Salé","maintenance", "2026-10-15"),
    ("SUV-07", "Renault Kadjar",         "suv",         "automatique",  520, "Agdal",              "active", None),
    ("SUV-08", "Volkswagen T-Roc",       "suv",         "automatique",  580, "Hay Riad",           "active", None),
    # ── Premium (700–1500 MAD) ────────────────────────────────────────────
    ("PRE-01", "Mercedes Classe A",      "premium",     "automatique",  800, "Agdal",              "active", None),
    ("PRE-02", "Mercedes Classe C",      "premium",     "automatique", 1200, "Aéroport Rabat-Salé","active", None),
    ("PRE-03", "BMW Série 3",            "premium",     "automatique", 1100, "Agdal",              "active", None),
    ("PRE-04", "Audi A3",               "premium",     "automatique",  900, "Hay Riad",           "active", None),
    # ── 4×4 (700–1000 MAD) ────────────────────────────────────────────────
    ("4X4-01", "Toyota Hilux",           "4x4",         "manuelle",     800, "Hay Riad",           "active", None),
    ("4X4-02", "Ford Ranger",            "4x4",         "automatique",  900, "Aéroport Rabat-Salé","active", None),
    # ── Utilitaires (300–600 MAD) ─────────────────────────────────────────
    ("UTL-01", "Renault Kangoo",         "utilitaire",  "manuelle",     350, "Hay Riad",           "active", None),
    ("UTL-02", "Fiat Doblo",             "utilitaire",  "manuelle",     320, "Agdal",              "active", None),
    ("UTL-03", "Renault Express",        "utilitaire",  "manuelle",     380, "Aéroport Rabat-Salé","active", None),
    ("UTL-04", "Citroën Berlingo",       "utilitaire",  "manuelle",     360, "Agdal",              "active", None),
]

PLATE_LETTERS = ["A", "B", "D", "H", "W"]  # أ ب د هـ و
CIN_PREFIX = ["A", "AA", "AB", "AD", "AE", "G", "BK", "BE", "CD", "DA", "EE"]
VIGNETTE = {"citadine": 350, "berline": 700, "suv": 1500, "4x4": 3000, "utilitaire": 700, "premium": 2000}

def plate(i: int) -> str:
    return f"{rng.randint(10000, 99999)}-{PLATE_LETTERS[i % len(PLATE_LETTERS)]}-1"


FLEET = []
for i, (vid, model, cat, tr, rate, loc, status, maint) in enumerate(FLEET_SPEC):
    circ = date(rng.randint(2019, 2024), rng.randint(1, 12), rng.randint(1, 28))
    km = int(max(0, (TODAY - circ).days) * rng.uniform(55, 90))
    ins = date(2026, rng.randint(10, 12), rng.randint(1, 28)) if i % 5 else TODAY + timedelta(days=rng.randint(5, 25))
    vt = (date(2026, rng.randint(11, 12), rng.randint(1, 28))) if (TODAY - circ).days > 4 * 365 else None
    FLEET.append(dict(code=vid, plate=plate(i), model=model, category=cat, transmission=tr,
                      location=loc, rate=rate, status=status, maintenance_until=maint,
                      circ=circ, km=km, insurance=ins, visite=vt))
BY_CODE = {v["code"]: v for v in FLEET}

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CUSTOMERS — Moroccan names + a few tourists                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
FIRST_M = ["Karim", "Youssef", "Omar", "Mehdi", "Hamza", "Amine", "Reda", "Anas", "Ayoub", "Ilyas",
           "Tarik", "Bilal", "Adam", "Yassine", "Othmane", "Walid", "Samir", "Driss", "Hicham",
           "Nabil", "Mounir", "Oussama", "Soufiane", "Zakaria", "Fouad", "Rachid", "Abdel",
           "Brahim", "Mouad", "Jamal", "Adil", "Khalid", "Taha", "Badr", "Ismail", "Anass"]
FIRST_F = ["Sara", "Imane", "Salma", "Nadia", "Khadija", "Fatima-Zahra", "Hind", "Meryem",
           "Souad", "Zineb", "Kenza", "Loubna", "Ghita", "Rim", "Aya", "Houda", "Nour",
           "Karima", "Siham", "Chaimae", "Wiam", "Asmae", "Lina", "Ines", "Samira", "Hanane"]
LASTS = ["Alaoui", "Bennani", "Tazi", "El Fassi", "Idrissi", "Berrada", "Chraibi", "Lahlou",
         "Benjelloun", "Sqalli", "Ouazzani", "Kettani", "Amrani", "Naciri", "Filali", "Rami",
         "Bouzidi", "El Amrani", "Hajji", "Mansouri", "El Khattabi", "Bouazza", "Tahiri",
         "Benchekroun", "El Harrak", "Moussaoui", "Kadiri", "Sefrioui", "El Idrissi", "Regragui"]
FOREIGN_FIRST = ["Jean-Marc", "Laura", "Pierre", "Sofia", "Luca", "Emma", "Carlos", "Anna",
                 "Thomas", "Marie", "Paolo", "Ingrid", "Ahmed", "Fatou", "Klaus", "Yuki"]
FOREIGN_LAST = ["Dupont", "Martin", "García", "Schmidt", "Rossi", "Svensson", "Diallo", "Chen"]

def cin() -> str:
    p = rng.choice(CIN_PREFIX)
    return p + str(rng.randint(10 ** (7 - len(p)), 10 ** (8 - len(p)) - 1))

def passport() -> str:
    return rng.choice(["XK", "AB", "YA", "PA", "FR", "GB", "DE", "IT"]) + str(rng.randint(1000000, 9999999))

CUSTOMERS = []
seen_cin = set()
for i in range(200):
    foreign = rng.random() < 0.12
    if foreign:
        fn = rng.choice(FOREIGN_FIRST)
        ln = rng.choice(FOREIGN_LAST)
        ident = passport()
    else:
        fn = rng.choice(FIRST_M if rng.random() < 0.55 else FIRST_F)
        ln = rng.choice(LASTS)
        ident = cin()
    while ident in seen_cin:
        ident = passport() if foreign else cin()
    seen_cin.add(ident)
    vip = i < 12 and not foreign  # 12 VIP clients
    CUSTOMERS.append(dict(
        code=f"C-{i + 1:03d}", cin=ident, name=f"{fn} {ln}",
        phone=f"0{rng.choice([6, 7])} {rng.randint(10,99)} {rng.randint(10,99)} {rng.randint(10,99)} {rng.randint(10,99)}",
        vip=vip,
        notes=rng.choice(["", "", "", "Touriste" if foreign else "", "Client entreprise (facture)",
                          "Préfère WhatsApp", "Demande souvent l'aéroport",
                          "Paiement à la remise des clés", "Client régulier" if vip else ""]),
        weight=4.0 if vip else (0.6 if foreign else 1.2)
    ))
WEIGHTS = [c["weight"] for c in CUSTOMERS]

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  RENTALS — July / August / September 2026, seasonal demand             ║
# ╚══════════════════════════════════════════════════════════════════════════╝
# July-August = haute saison (MRE + touristes, high occupancy), Sept = rentrée (drops)
CHANNELS = ["WhatsApp", "WhatsApp", "WhatsApp", "Téléphone", "Comptoir", "Facebook", "Instagram", "Site web", "Booking.com"]

def season_factor(d: date) -> tuple[float, float]:
    """(mean idle days between rentals, price multiplier)."""
    if d.month == 7:
        return 0.6, 1.25   # peak summer
    if d.month == 8:
        return 0.5, 1.30   # peak + Eid
    if d.month == 9 and d.day <= 15:
        return 1.5, 1.10   # end of summer
    return 2.5, 1.0        # rentrée

def rent_len(d: date) -> int:
    if d.month in (7, 8):
        return rng.choice([2, 3, 3, 4, 5, 5, 7, 7, 10, 14, 14, 21])
    return rng.choice([1, 2, 2, 3, 3, 4, 5, 7])

def price(rate: int, d: date, days: int) -> int:
    _, f = season_factor(d)
    disc = 0.90 if days >= 14 else 0.93 if days >= 7 else 1.0
    return int(round(rate * f * disc * rng.uniform(0.95, 1.05) / 10) * 10)

# Also load V1 bookings.csv for demo-scenario compatibility
DEMO_BOOKINGS = []
try:
    with open(HERE / "bookings.csv", encoding="utf-8") as f:
        for b in csv.DictReader(f):
            DEMO_BOOKINGS.append(b)
except FileNotFoundError:
    pass

def _overlap(a0, a1, b0, b1):
    return a0 <= b1 and b0 <= a1

def gen_rentals() -> list[dict]:
    rows = []
    for v in FLEET:
        if v["status"] == "maintenance":
            maint_end = date.fromisoformat(v["maintenance_until"]) if v["maintenance_until"] else END
            d = max(START, maint_end + timedelta(days=1))
        else:
            d = START + timedelta(days=rng.randint(0, 3))
        occupied = []  # (start, end) ranges
        # inject demo bookings for this vehicle
        for b in DEMO_BOOKINGS:
            if b["vehicle_id"] == v["code"]:
                bs, be = date.fromisoformat(b["start_date"]), date.fromisoformat(b["end_date"])
                occupied.append((bs, be))
                c = rng.choices(CUSTOMERS, weights=WEIGHTS)[0]
                rows.append(dict(plate=v["plate"], code=v["code"], cin=c["cin"],
                                 price=price(v["rate"], bs, max(1, (be - bs).days)),
                                 out=bs, back=be, channel=rng.choice(CHANNELS),
                                 status="terminee" if be <= TODAY else "en_cours" if bs <= TODAY else "reservee"))
        while d <= END:
            idle_mean, _ = season_factor(d)
            d += timedelta(days=max(0, int(rng.expovariate(1 / max(0.3, idle_mean)))))
            if d > END:
                break
            n = rent_len(d)
            end = d + timedelta(days=n)
            if end > END + timedelta(days=14):
                break
            if any(_overlap(d, end, a, b) for a, b in occupied):
                d += timedelta(days=1)
                continue
            occupied.append((d, end))
            c = rng.choices(CUSTOMERS, weights=WEIGHTS)[0]
            rows.append(dict(plate=v["plate"], code=v["code"], cin=c["cin"],
                             price=price(v["rate"], d, n), out=d, back=end,
                             channel=rng.choice(CHANNELS),
                             status="terminee" if end <= TODAY else "en_cours" if d <= TODAY else "reservee"))
            d = end + timedelta(days=rng.choice([0, 0, 1]))
    rows.sort(key=lambda r: (r["out"], r["plate"]))
    for i, r in enumerate(rows, 1):
        r["id"] = f"L-{i:05d}"
    return rows

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  EXPENSES — per vehicle + agency overheads                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
EXP_CATS = ["Leasing", "Assurance", "Vignette", "Vidange", "Pneus", "Réparation", "Lavage",
            "Visite technique", "Carburant", "Loyer", "Salaires", "Électricité & eau",
            "Internet & téléphone", "Marketing", "Comptabilité", "Logiciel"]
GARAGES = ["Garage Atlas Agdal", "Auto Service Hay Riad", "Speedy Rabat", "Norauto Rabat", "Pneus Plus Témara"]

def gen_expenses(rentals: list[dict]) -> list[dict]:
    rows = []
    by_car: dict[str, list[dict]] = {}
    for r in rentals:
        by_car.setdefault(r["code"], []).append(r)

    for v in FLEET:
        code, plate_ = v["code"], v["plate"]
        leased = v["circ"].year >= 2023
        for m in [date(2026, 7, 1), date(2026, 8, 1), date(2026, 9, 1)]:
            last = min(TODAY, (m.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1))
            if leased:
                rows.append(dict(date=m.replace(day=5), plate=plate_, cat="Leasing",
                                 amount=int(v["rate"] * 7.5 // 10 * 10),
                                 supplier="Wafasalaf LOA", note=f"Échéance {m.strftime('%m/%Y')}"))
            month_rentals = [r for r in by_car.get(code, []) if m <= r["back"] <= last]
            if month_rentals:
                rows.append(dict(date=last, plate=plate_, cat="Lavage",
                                 amount=len(month_rentals) * 40,
                                 supplier="Lavage Express Agdal", note=f"{len(month_rentals)} lavages"))
            # oil change every ~45 rental-days
            total_days = sum((r["back"] - r["out"]).days for r in by_car.get(code, []) if r["back"] <= last)
            if total_days > 0 and total_days % 45 < 15 and m.month == 8:
                rows.append(dict(date=m.replace(day=rng.randint(5, 25)), plate=plate_, cat="Vidange",
                                 amount=rng.randint(45, 80) * 10,
                                 supplier=rng.choice(GARAGES), note="Vidange + filtres"))
            if rng.random() < 0.06:
                rows.append(dict(date=m.replace(day=rng.randint(2, 27)), plate=plate_, cat="Réparation",
                                 amount=rng.randint(8, 50) * 100,
                                 supplier=rng.choice(GARAGES),
                                 note=rng.choice(["Embrayage", "Freins", "Carrosserie", "Batterie", "Climatisation"])))
            if rng.random() < 0.1:
                rows.append(dict(date=m.replace(day=rng.randint(2, 27)), plate=plate_, cat="Carburant",
                                 amount=rng.randint(3, 8) * 100,
                                 supplier="Afriquia", note="Plein avant livraison aéroport"))

    # Monthly agency overheads
    for m in [date(2026, 7, 1), date(2026, 8, 1), date(2026, 9, 1)]:
        summer = m.month in (7, 8)
        rows += [
            dict(date=m.replace(day=1),  plate="", cat="Loyer",   amount=12000, supplier="SCI Agdal", note="Agence Agdal"),
            dict(date=m.replace(day=1),  plate="", cat="Loyer",   amount=7000,  supplier="Particulier", note="Point Hay Riad"),
            dict(date=m.replace(day=1),  plate="", cat="Loyer",   amount=5000,  supplier="ONDA", note="Comptoir aéroport"),
            dict(date=m.replace(day=28), plate="", cat="Salaires", amount=32000 + (8000 if summer else 0),
                 supplier="Personnel", note="4 agents + renfort été" if summer else "4 agents"),
            dict(date=m.replace(day=12), plate="", cat="Électricité & eau", amount=rng.randint(80, 150) * 10,
                 supplier="Redal", note=""),
            dict(date=m.replace(day=15), plate="", cat="Internet & téléphone", amount=780, supplier="Maroc Telecom",
                 note="Fibre + 4 lignes"),
            dict(date=m.replace(day=20), plate="", cat="Marketing",
                 amount=rng.randint(20, 35) * 100 + (3000 if summer else 0),
                 supplier="Meta Ads / Google Ads", note="Campagne été" if summer else "Facebook / Instagram"),
            dict(date=m.replace(day=25), plate="", cat="Comptabilité", amount=2500, supplier="Cabinet Fiduciaire", note=""),
            dict(date=m.replace(day=3),  plate="", cat="Logiciel", amount=400, supplier="Hébergement AutoFlow", note="VPS + domaine"),
        ]
    rows = [r for r in rows if START <= r["date"] <= TODAY]
    rows.sort(key=lambda r: (r["date"], r["plate"], r["cat"]))
    return rows

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  APPOINTMENTS                                                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝
APPT_TYPES = ["Entretien garage", "Visite technique", "Renouvellement assurance",
              "Expertise sinistre", "Rendez-vous client", "Fournisseur"]

def gen_appointments() -> list[dict]:
    rows = []
    d = START
    while d <= END:
        if d.weekday() < 6 and rng.random() < 0.35:
            t = rng.choices(APPT_TYPES, weights=[4, 1, 1, 1, 3, 1])[0]
            v = rng.choice(FLEET)
            c = rng.choice(CUSTOMERS)
            rows.append(dict(date=d, time=f"{rng.choice([9, 10, 11, 14, 15, 16, 17])}:{rng.choice(['00', '30'])}",
                             type=t, plate=v["plate"] if t not in ("Rendez-vous client", "Fournisseur") else "",
                             cin=c["cin"] if t == "Rendez-vous client" else "",
                             status="fait" if d < TODAY else "prévu",
                             note={"Entretien garage": "Révision", "Rendez-vous client": rng.choice(
                                 ["Contrat entreprise", "Location longue durée", "Mariage — 3 berlines", "Touriste — navette aéroport"]),
                                   "Fournisseur": rng.choice(["Leasing : 2 citadines", "Assureur : devis flotte", "Pneus hiver"]),
                                   "Expertise sinistre": "Rayure portière", "Visite technique": "",
                                   "Renouvellement assurance": ""}[t]))
        d += timedelta(days=1)
    rows.sort(key=lambda r: (r["date"], r["time"]))
    return rows

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  EXCEL WRITER                                                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝
NAVY, TEAL = "0B1F3A", "0E9C99"
HEAD_FONT = Font(bold=True, color="FFFFFF", name="Calibri", size=11)
HEAD_FILL = PatternFill("solid", fgColor=NAVY)
CALC_FILL = PatternFill("solid", fgColor=TEAL)
THIN = Side(style="thin", color="D8DCE3")

def _sheet(wb, title, headers, rows, widths, calc_cols=(), date_cols=(), money_cols=(), table=True):
    ws = wb.create_sheet(title)
    ws.append(headers)
    for r in rows:
        ws.append(r)
    for j, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=j)
        c.font = HEAD_FONT
        c.fill = CALC_FILL if h in calc_cols else HEAD_FILL
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = Border(bottom=THIN)
        ws.column_dimensions[get_column_letter(j)].width = widths.get(h, 14)
        if h in date_cols:
            for i in range(2, len(rows) + 2):
                ws.cell(row=i, column=j).number_format = "DD/MM/YYYY"
        if h in money_cols:
            for i in range(2, len(rows) + 2):
                ws.cell(row=i, column=j).number_format = '#,##0" MAD"'
    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 22
    if table and rows:
        ref = f"A1:{get_column_letter(len(headers))}{len(rows) + 1}"
        t = Table(displayName=f"T_{title}", ref=ref)
        t.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showRowStripes=True)
        ws.add_table(t)
    return ws

def write(rentals, expenses, appts) -> None:
    wb = Workbook()
    wb.remove(wb.active)

    # Locations
    hdr = ["N_LOCATION", "MATRICULE", "CIN", "PRIX_JOUR", "DATE_SORTIE", "DATE_ENTREE",
           "PERIODE", "MONTANT", "DISPONIBILITE", "CANAL", "STATUT"]
    rows = []
    for i, r in enumerate(rentals, 2):
        rows.append([r["id"], r["plate"], r["cin"], r["price"], r["out"], r["back"],
                     f"=MAX(1,F{i}-E{i})", f"=D{i}*G{i}",
                     f'=IF(TODAY()<E{i},"À venir",IF(TODAY()<F{i},"En cours","Terminée"))',
                     r["channel"],
                     {"terminee": "Terminée", "en_cours": "En cours", "reservee": "Réservée"}[r["status"]]])
    ws = _sheet(wb, "Locations", hdr, rows,
                {"N_LOCATION": 13, "MATRICULE": 14, "CIN": 13, "DATE_SORTIE": 14,
                 "DATE_ENTREE": 14, "DISPONIBILITE": 15, "CANAL": 13, "MONTANT": 14},
                calc_cols=("PERIODE", "MONTANT", "DISPONIBILITE"),
                date_cols=("DATE_SORTIE", "DATE_ENTREE"), money_cols=("PRIX_JOUR", "MONTANT"))
    n = len(rows) + 1
    ws.conditional_formatting.add(f"I2:I{n}", CellIsRule(operator="equal", formula=['"En cours"'],
                                                          fill=PatternFill("solid", fgColor="FEF3C7")))
    ws.conditional_formatting.add(f"I2:I{n}", CellIsRule(operator="equal", formula=['"À venir"'],
                                                          fill=PatternFill("solid", fgColor="DDF3F2")))

    # Flotte
    hdr = ["CODE", "MATRICULE", "MODELE", "CATEGORIE", "BOITE", "AGENCE", "PRIX_JOUR",
           "STATUT", "FIN_MAINTENANCE", "MISE_EN_CIRCULATION", "KM",
           "ASSURANCE_EXPIRE", "VISITE_TECHNIQUE_EXPIRE", "DISPONIBILITE"]
    rows = []
    for i, v in enumerate(FLEET, 2):
        rows.append([v["code"], v["plate"], v["model"], v["category"], v["transmission"],
                     v["location"], v["rate"], v["status"],
                     date.fromisoformat(v["maintenance_until"]) if v["maintenance_until"] else None,
                     v["circ"], v["km"], v["insurance"], v["visite"],
                     f'=IF(H{i}="maintenance","Maintenance",IF(COUNTIFS(Locations!B:B,B{i},Locations!E:E,"<="&TODAY(),Locations!F:F,">"&TODAY())>0,"Louée","Disponible"))'])
    ws = _sheet(wb, "Flotte", hdr, rows,
                {"MODELE": 22, "MATRICULE": 14, "AGENCE": 22, "FIN_MAINTENANCE": 16,
                 "MISE_EN_CIRCULATION": 20, "ASSURANCE_EXPIRE": 17,
                 "VISITE_TECHNIQUE_EXPIRE": 23, "DISPONIBILITE": 15},
                calc_cols=("DISPONIBILITE",),
                date_cols=("FIN_MAINTENANCE", "MISE_EN_CIRCULATION", "ASSURANCE_EXPIRE",
                           "VISITE_TECHNIQUE_EXPIRE"),
                money_cols=("PRIX_JOUR",))
    n = len(rows) + 1
    ws.conditional_formatting.add(f"N2:N{n}", CellIsRule(operator="equal", formula=['"Disponible"'],
                                                          fill=PatternFill("solid", fgColor="D1FAE5")))
    ws.conditional_formatting.add(f"N2:N{n}", CellIsRule(operator="equal", formula=['"Louée"'],
                                                          fill=PatternFill("solid", fgColor="FEF3C7")))
    ws.conditional_formatting.add(f"N2:N{n}", CellIsRule(operator="equal", formula=['"Maintenance"'],
                                                          fill=PatternFill("solid", fgColor="FFE4E6")))
    ws.conditional_formatting.add(f"L2:M{n}", FormulaRule(formula=[f"AND(L2<>\"\",L2-TODAY()<30)"],
                                                           fill=PatternFill("solid", fgColor="FFE4E6")))

    # Clients
    _sheet(wb, "Clients", ["CIN", "NOM", "TELEPHONE", "VIP", "NOTES", "CODE"],
           [[c["cin"], c["name"], c["phone"], "oui" if c["vip"] else "non", c["notes"], c["code"]] for c in CUSTOMERS],
           {"NOM": 24, "TELEPHONE": 16, "NOTES": 34})

    # Depenses
    ws = _sheet(wb, "Depenses", ["DATE", "MATRICULE", "CATEGORIE", "MONTANT", "FOURNISSEUR", "NOTE"],
                [[e["date"], e["plate"] or None, e["cat"], e["amount"], e["supplier"], e["note"]] for e in expenses],
                {"CATEGORIE": 20, "FOURNISSEUR": 24, "NOTE": 30},
                date_cols=("DATE",), money_cols=("MONTANT",))
    dv = DataValidation(type="list", formula1='"' + ",".join(EXP_CATS) + '"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"C2:C{len(expenses) + 500}")

    # RendezVous
    ws = _sheet(wb, "RendezVous", ["DATE", "HEURE", "TYPE", "MATRICULE", "CIN", "STATUT", "NOTE"],
                [[a["date"], a["time"], a["type"], a["plate"] or None, a["cin"] or None,
                  a["status"], a["note"]] for a in appts],
                {"TYPE": 24, "NOTE": 36}, date_cols=("DATE",))
    dv = DataValidation(type="list", formula1='"' + ",".join(APPT_TYPES) + '"')
    ws.add_data_validation(dv)
    dv.add(f"C2:C{len(appts) + 300}")

    # Guide
    guide = [
        ("Locations", "MATRICULE", "Plaque du véhicule (doit exister dans Flotte)"),
        ("Locations", "CIN", "CIN marocaine (ex. AB123456) ou passeport (ex. XK1234567)"),
        ("Locations", "PRIX_JOUR", "Prix facturé par jour, en MAD"),
        ("Locations", "DATE_SORTIE", "Le véhicule quitte l'agence (début de location)"),
        ("Locations", "DATE_ENTREE", "Le véhicule revient à l'agence (fin de location)"),
        ("Locations", "PERIODE", "Calculé : DATE_ENTREE − DATE_SORTIE (jours, minimum 1)"),
        ("Locations", "MONTANT", "Calculé : PRIX_JOUR × PERIODE"),
        ("Locations", "DISPONIBILITE", "Calculé : À venir / En cours / Terminée selon la date du jour"),
        ("Flotte", "DISPONIBILITE", "Calculé : Disponible / Louée / Maintenance aujourd'hui"),
        ("Depenses", "MATRICULE", "Vide = frais généraux de l'agence (loyer, salaires…)"),
        ("Depenses", "CATEGORIE", "Liste fermée : " + ", ".join(EXP_CATS)),
        ("RendezVous", "TYPE", "Liste fermée : " + ", ".join(APPT_TYPES)),
        ("—", "Colonnes vertes", "Formules : ne pas saisir. AutoFlow les recalcule à l'import."),
    ]
    _sheet(wb, "Guide", ["FEUILLE", "COLONNE", "DESCRIPTION"],
           [list(g) for g in guide], {"FEUILLE": 14, "COLONNE": 20, "DESCRIPTION": 80}, table=False)
    wb.move_sheet("Guide", offset=-5)

    info = wb.create_sheet("Lisez-moi", 0)
    info["A1"] = "AutoFlow Pro — base de données de l'agence"
    info["A1"].font = Font(bold=True, size=16, color=NAVY)
    info["A3"] = f"Données FICTIVES générées le {TODAY.strftime('%d/%m/%Y')} (graine 2026)"
    info["A4"] = f"Période : {START.strftime('%d/%m/%Y')} → {END.strftime('%d/%m/%Y')} (3 mois, haute saison)"
    info["A5"] = f"{len(FLEET)} véhicules · {len(CUSTOMERS)} clients · {len(rentals)} locations · {len(expenses)} dépenses · {len(appts)} rendez-vous."
    info["A6"] = "Tarifs basés sur les prix réels du marché marocain 2025-2026 (RAKB, OneClickDrive, Avito, agences Rabat)."
    info["A7"] = "Importer ce fichier dans AutoFlow : Administration → Données Excel. Les colonnes vertes sont calculées."
    info.column_dimensions["A"].width = 110
    wb.save(OUT)


def main() -> None:
    rentals = gen_rentals()
    expenses = gen_expenses(rentals)
    appts = gen_appointments()
    write(rentals, expenses, appts)
    (HERE / "workbook_manifest.json").write_text(json.dumps({
        "generated_for": TODAY.isoformat(), "seed": 2026,
        "vehicles": len(FLEET), "customers": len(CUSTOMERS),
        "rentals": len(rentals), "expenses": len(expenses),
        "appointments": len(appts),
        "period": [START.isoformat(), END.isoformat()],
        "market_sources": ["rakb.ma", "oneclickdrive.ma", "avito.ma", "goride.ma", "casaride.ma",
                           "mymobirent.com", "banyolti.com", "rayhane-cars.net"]
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{OUT.name}: {len(FLEET)} véhicules, {len(CUSTOMERS)} clients, {len(rentals)} locations, "
          f"{len(expenses)} dépenses, {len(appts)} rendez-vous")


if __name__ == "__main__":
    main()

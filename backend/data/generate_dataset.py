"""Generate a realistic *fictional* dataset for a Rabat car-rental agency.

Deterministic (seeded) so the demo is reproducible. Produces:
  fleet.csv      24 vehicles — Moroccan market mix (Dacia, Renault, Hyundai, Kia, Peugeot, Toyota…)
  bookings.csv   ~80 confirmed rentals Sept → Dec 2026, no overlap per vehicle
  customers.csv  40 fictional customers (masked phones), 6 flagged "régulier"
  history.json   45 inbound messages (FR / light Darija) spread over the last 6 weeks,
                 each with a scripted human outcome so the replay looks lived-in.

The 8 vehicles + 6 bookings used by demo scenarios A–E are kept verbatim and their
date windows are protected, so the live demo and the tests stay deterministic.

Run:  python data/generate_dataset.py   (from backend/)
"""
from __future__ import annotations

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
rng = random.Random(2026)

# --------------------------------------------------------------------------- #
# Fleet
# --------------------------------------------------------------------------- #
CORE_FLEET = [  # id, category, model, transmission, location, status, maintenance_until, rate
    ("CIT-01", "citadine", "Dacia Sandero", "manuelle", "Agdal", "active", "", 250),
    ("CIT-02", "citadine", "Renault Clio", "manuelle", "Hay Riad", "active", "", 260),
    ("CIT-03", "citadine", "Hyundai i10", "manuelle", "Agdal", "active", "", 230),
    ("BER-01", "berline", "Dacia Logan", "manuelle", "Agdal", "active", "", 320),
    ("BER-02", "berline", "Peugeot 308", "automatique", "Agdal", "active", "", 400),
    ("SUV-01", "suv", "Dacia Duster", "automatique", "Agdal", "maintenance", "2026-10-22", 450),
    ("SUV-02", "suv", "Hyundai Tucson", "automatique", "Hay Riad", "active", "", 550),
    ("UTL-01", "utilitaire", "Renault Kangoo", "manuelle", "Hay Riad", "active", "", 380),
]
EXTRA_FLEET = [
    ("CIT-04", "citadine", "Kia Picanto", "manuelle", "Hay Riad", "active", "", 240),
    ("CIT-05", "citadine", "Peugeot 208", "manuelle", "Agdal", "active", "", 280),
    ("CIT-06", "citadine", "Toyota Yaris", "automatique", "Agdal", "active", "", 320),
    ("CIT-07", "citadine", "Volkswagen Polo", "manuelle", "Aeroport Rabat-Sale", "active", "", 270),
    ("CIT-08", "citadine", "Renault Clio", "automatique", "Hay Riad", "active", "", 300),
    ("CIT-09", "citadine", "Dacia Sandero Stepway", "manuelle", "Aeroport Rabat-Sale", "active", "", 265),
    ("BER-03", "berline", "Hyundai Accent", "automatique", "Hay Riad", "active", "", 380),
    ("BER-04", "berline", "Toyota Corolla", "automatique", "Agdal", "active", "", 450),
    ("BER-05", "berline", "Skoda Octavia", "automatique", "Aeroport Rabat-Sale", "active", "", 480),
    ("BER-06", "berline", "Mercedes Classe A", "automatique", "Agdal", "active", "", 700),
    ("SUV-03", "suv", "Kia Sportage", "automatique", "Agdal", "active", "", 600),
    ("SUV-04", "suv", "Dacia Duster", "manuelle", "Aeroport Rabat-Sale", "active", "", 420),
    ("SUV-05", "suv", "Hyundai Creta", "automatique", "Hay Riad", "active", "", 520),
    ("SUV-06", "suv", "Peugeot 3008", "automatique", "Agdal", "maintenance", "2026-10-05", 650),
    ("4X4-01", "4x4", "Toyota Hilux", "manuelle", "Hay Riad", "active", "", 800),
    ("UTL-02", "utilitaire", "Fiat Doblo", "manuelle", "Agdal", "active", "", 360),
]
FLEET = CORE_FLEET + EXTRA_FLEET

CORE_BOOKINGS = [
    ("B-001", "CIT-01", "2026-10-11", "2026-10-14"),
    ("B-002", "SUV-02", "2026-10-18", "2026-10-22"),
    ("B-003", "BER-01", "2026-10-13", "2026-10-16"),
    ("B-004", "CIT-02", "2026-10-24", "2026-10-26"),
    ("B-005", "UTL-01", "2026-10-20", "2026-10-21"),
    ("B-006", "BER-02", "2026-11-02", "2026-11-05"),
    # extra fleet booked during the scenario windows so B (SUV → alternative) and E (berline auto → alternative) hold
    ("B-007", "SUV-03", "2026-10-19", "2026-10-24"),
    ("B-008", "SUV-05", "2026-10-17", "2026-10-28"),
    ("B-009", "SUV-04", "2026-10-20", "2026-10-23"),
    ("B-010", "SUV-06", "2026-10-21", "2026-10-26"),
    ("B-011", "BER-03", "2026-11-01", "2026-11-07"),
    ("B-012", "BER-04", "2026-11-02", "2026-11-08"),
    ("B-013", "BER-05", "2026-10-31", "2026-11-06"),
    ("B-014", "BER-06", "2026-11-03", "2026-11-05"),
]
# windows the demo scenarios rely on: (vehicle, start, end) must stay FREE
PROTECTED_FREE = [
    ("CIT-03", "2026-10-12", "2026-10-15"),   # scenario A
    ("CIT-02", "2026-10-12", "2026-10-15"),
    ("BER-02", "2026-10-20", "2026-10-27"),   # scenario B alternative
    ("BER-01", "2026-10-20", "2026-10-27"),
    ("CIT-03", "2026-10-24", "2026-10-26"),   # scenario C completion
    ("BER-01", "2026-11-03", "2026-11-06"),   # scenario E alternative
]

PROTECTED_RANGES = [(date(2026, 10, 9), date(2026, 10, 29)), (date(2026, 11, 1), date(2026, 11, 8))]

# --------------------------------------------------------------------------- #
# Customers
# --------------------------------------------------------------------------- #
FIRST = ["Karim", "Sara", "Youssef", "Imane", "Omar", "Salma", "Mehdi", "Nadia", "Hamza", "Khadija", "Amine", "Fatima-Zahra",
         "Reda", "Hind", "Anas", "Meryem", "Ayoub", "Souad", "Ilyas", "Zineb", "Tarik", "Kenza", "Bilal", "Loubna", "Adam",
         "Ghita", "Yassine", "Rim", "Othmane", "Aya", "Samir", "Houda", "Walid", "Nour", "Jean-Marc", "Laura", "Ahmed", "Lina", "Driss", "Ines"]
LAST_INITIAL = list("ABCDEFGHKLMNORSTZ")
CUSTOMERS = []
for i in range(40):
    fn = FIRST[i]
    name = f"{fn} {rng.choice(LAST_INITIAL)}." if rng.random() > 0.15 else f"Famille {rng.choice(['Alaoui', 'Bennani', 'Tazi', 'El Fassi', 'Idrissi', 'Berrada'])}"
    if i == 1:
        name = "Famille Alaoui"
    vip = i in (1, 4, 9, 14, 22, 31)
    phone = f"0{rng.choice([6, 7])} XX XX XX {i + 1:02d}"
    notes = rng.choice(["", "", "", "Préfère WhatsApp", "Client entreprise (facture)", "Demande souvent l'aéroport", "Paiement à la remise des clés"])
    if vip:
        notes = "Clients réguliers (VIP)" + (" — " + notes if notes else "")
    CUSTOMERS.append((f"C-{i + 1:03d}", name, phone, "true" if vip else "false", notes))

# --------------------------------------------------------------------------- #
# Bookings (no overlap per vehicle, protected windows kept free)
# --------------------------------------------------------------------------- #
def _d(s: str) -> date:
    return date.fromisoformat(s)


def _overlap(a0, a1, b0, b1) -> bool:
    return a0 <= b1 and b0 <= a1


def gen_bookings() -> list[tuple[str, str, str, str]]:
    per_vehicle: dict[str, list[tuple[date, date]]] = {v[0]: [] for v in FLEET}
    out = list(CORE_BOOKINGS)
    for _, vid, s, e in CORE_BOOKINGS:
        per_vehicle[vid].append((_d(s), _d(e)))
    for vid, s, e in PROTECTED_FREE:
        per_vehicle[vid].append((_d(s) - timedelta(days=1), _d(e) + timedelta(days=1)))  # reserve as "blocked" for generation
    n = 15
    season = [(date(2026, 9, 1), date(2026, 12, 31))]
    tries = 0
    while len(out) < 80 and tries < 5000:
        tries += 1
        v = rng.choice(FLEET)
        if v[5] == "maintenance":
            continue
        start = season[0][0] + timedelta(days=rng.randint(0, 120))
        length = rng.choice([1, 2, 2, 3, 3, 4, 5, 7, 10, 14])
        end = start + timedelta(days=length)
        if any(_overlap(start, end + timedelta(days=1), b0, b1) for b0, b1 in per_vehicle[v[0]]):
            continue
        per_vehicle[v[0]].append((start, end))
        out.append((f"B-{n:03d}", v[0], start.isoformat(), end.isoformat()))
        n += 1
    out.sort(key=lambda b: b[2])
    return out


# --------------------------------------------------------------------------- #
# Inbound history messages — parsable by the rules engine, varied phrasing
# --------------------------------------------------------------------------- #
CATS = ["citadine", "berline", "suv", "citadine", "citadine", "berline", "utilitaire", "4x4"]
LOCS = ["Agdal", "Hay Riad", "l'aéroport Rabat-Salé", "Rabat"]
MONTHS_FR = {7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"}
OPENERS = ["Bonjour,", "Salam,", "Bonsoir,", "Slt,", "Bonjour l'équipe,", "Salam alikoum,", "Hello,"]
CLOSERS = ["Merci.", "Merci d'avance !", "C'est possible ?", "Vous avez ça ?", "Dites-moi le prix svp.", "Merci bcp", "Je suis preneur si dispo.", ""]
TEMPLATES = [
    "{op} je voudrais louer une {cat} du {d1} au {d2} {mon}, prise à {loc}. {cl}",
    "{op} dispo une {cat} {tr}du {d1}/{m} au {d2}/{m} ? Départ {loc}. {cl}",
    "{op} besoin d'une {cat} {tr}pour la période du {d1} au {d2} {mon}, retour {loc}. {cl}",
    "{op} c'est combien une {cat} du {d1} au {d2} {mon} à {loc} ? {cl}",
    "{op} je cherche une voiture {cat} {tr}du {d1} au {d2} {mon}. Prise {loc}. {cl}",
    "{op} location {cat} {d1}-{d2} {mon} svp, {loc}. {cl}",
]
SPECIALS = [
    ("{op} on est des clients réguliers, une {cat} du {d1} au {d2} {mon} à {loc}, un petit geste sur le prix serait apprécié 🙏", ["discount", "vip"]),
    ("{op} une voiture pour ce week-end à {loc}, vous avez quoi ? {cl}", ["ambiguous"]),
    ("{op} dispo une {cat} pour le week-end prochain ? {cl}", ["ambiguous"]),
    ("{op} je voudrais une {cat} le {d1} {mon} pour 3 jours, {loc}. Est-ce qu'il y a une remise pour 3 jours ? {cl}", ["discount"]),
    ("{op} le véhicule rendu hier avait un problème de frein et personne ne répond au téléphone. Ce n'est pas normal.", ["complaint"]),
    ("{op} j'ai un problème avec la facture de la semaine dernière, on m'a compté 2 jours de trop. Merci de me rappeler.", ["complaint"]),
    ("{op} je veux modifier ma réservation du {d1} {mon} : décaler au {d2} {mon} si possible. {cl}", ["modification"]),
    ("{op} quelle est la caution et le kilométrage inclus pour une {cat} ? {cl}", ["info"]),
    ("{op} une {cat} {tr}du {d1} au {d2} {mon} à {loc}, j'ai un budget de 3000 dh max. {cl}", []),
    ("{op} une {cat} du {d1} {mon} au {d2} {mon2} (3 semaines), {loc}. {cl}", ["long"]),
]
OUTCOMES = {  # scripted human behaviour when replaying history (probabilities)
    "standard": [("approve_accept", .45), ("approve_decline", .15), ("approve_pending", .3), ("reject", .1)],
    "manager": [("approve_accept", .4), ("approve_pending", .3), ("reject", .3)],
    "clarify": [("complete_accept", .5), ("complete_pending", .3), ("close", .2)],
    "complaint": [("close", 1.0)],
}


def _pick(dist):
    r, acc = rng.random(), 0
    for k, p in dist:
        acc += p
        if r <= acc:
            return k
    return dist[-1][0]


def gen_history(today: date) -> list[dict]:
    out = []
    for i in range(45):
        days_ago = round(rng.uniform(1, 42), 2)
        received = today - timedelta(days=days_ago)
        # requested pickup 3–30 days after the message
        d1 = received + timedelta(days=rng.randint(3, 30))
        length = rng.choice([1, 2, 2, 3, 3, 4, 5, 7])
        d2 = d1 + timedelta(days=length)
        if d2.month != d1.month:  # keep both dates in the same month so "du X au Y <mois>" stays valid
            d1 = date(d1.year, d1.month, max(1, 27 - length))
            d2 = d1 + timedelta(days=length)
        cat = rng.choice(CATS)
        # keep replayed bookings out of the windows the live demo scenarios rely on
        if cat in ("citadine", "berline") and any(_overlap(d1, d2, a, b) for a, b in PROTECTED_RANGES):
            d1 = date(2026, 11, 10) + timedelta(days=rng.randint(0, 12))
            d2 = d1 + timedelta(days=length)
        tr = rng.choice(["", "", "automatique ", "manuelle "])
        loc = rng.choice(LOCS)
        cust = rng.choice(CUSTOMERS)
        fields = dict(op=rng.choice(OPENERS), cat=cat, tr=tr, d1=d1.day, d2=d2.day, m=f"{d1.month:02d}",
                      mon=MONTHS_FR.get(d1.month, "octobre"), mon2=MONTHS_FR.get((d1 + timedelta(days=21)).month, "novembre"),
                      loc=loc, cl=rng.choice(CLOSERS))
        kind = "standard"
        if rng.random() < 0.3:
            tpl, tags = rng.choice(SPECIALS)
            if "long" in tags:
                d2 = d1 + timedelta(days=21); fields["d2"] = d2.day
            if "pour 3 jours" in tpl:
                d2 = d1 + timedelta(days=3)
            if d1.month != d2.month and "{d2} {mon}" in tpl:  # keep same-month phrasing simple
                fields["d2"] = min(d2.day, 28)
            kind = "complaint" if "complaint" in tags else "clarify" if "ambiguous" in tags or "info" in tags else "manager" if "discount" in tags or "long" in tags else "standard"
        else:
            tpl = rng.choice(TEMPLATES)
        if cust[3] == "true" and kind == "standard" and rng.random() < 0.5:
            tpl = tpl.rstrip() + " On a déjà loué chez vous plusieurs fois."
        msg = tpl.format(**fields).replace("  ", " ").strip()
        out.append({
            "days_ago": days_ago,
            "customer": cust[1],
            "channel": rng.choice(["whatsapp", "whatsapp", "whatsapp", "facebook", "phone", "form", "walk-in"]),
            "message": msg,
            "outcome": _pick(OUTCOMES[kind]),
            "complete_fields": {"pickup_date": d1.isoformat(), "return_date": d2.isoformat(), "vehicle_category": cat,
                                "pickup_location": "Agdal" if "Agdal" in loc or loc == "Rabat" else "Hay Riad" if "Riad" in loc else "Aeroport Rabat-Sale"},
        })
    out.sort(key=lambda h: -h["days_ago"])
    return out


def main(today: date | None = None) -> None:
    today = today or date(2026, 9, 21)
    with open(HERE / "fleet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["vehicle_id", "category", "model", "transmission", "location", "status", "maintenance_until", "daily_rate_mad"])
        w.writerows(FLEET)
    with open(HERE / "bookings.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["booking_id", "vehicle_id", "start_date", "end_date", "status"])
        w.writerows([(*b, "confirmed") for b in gen_bookings()])
    with open(HERE / "customers.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["customer_id", "name", "phone_masked", "is_vip", "notes"])
        w.writerows(CUSTOMERS)
    (HERE / "history.json").write_text(json.dumps(gen_history(today), ensure_ascii=False, indent=1), encoding="utf-8")
    print("fleet:", len(FLEET), "| customers:", len(CUSTOMERS), "| history: 45 messages → data/")


if __name__ == "__main__":
    main()

# 08 — Demo Plan

**Goal:** a 6–8 minute live demo that works with zero access to real agency data, tells the Struggle → Workflow → Supervision → Result story, and never claims a measured outcome.
**Audience:** agency owner/manager first; jury and recruiters second.
**Rule:** every screen shows the banner **« Données de démonstration — aucun client réel »**.

---

## 1. Demo narrative (what the audience sees)

| Step | On screen | What it proves | Time |
|---|---|---|---|
| 0 | Dashboard, empty queue, banner "Données de démonstration" | Calm starting point; honest framing | 0:20 |
| 1 | A WhatsApp-style message pasted into "Nouvelle demande" | Requests arrive unstructured | 0:30 |
| 2 | Intake result card: intent, dates, category, location, confidence, missing fields | The system *understands*, and says what it doesn't know | 0:45 |
| 3 | Availability result against the mock fleet table (visible) | Truthful check, explainable | 0:45 |
| 4 | Second request → requested SUV unavailable → alternative proposed with reason | The system helps sell, doesn't just say no | 0:45 |
| 5 | Draft reply in French; staff edits one word; clicks "Envoyer" (simulated) | Human sends; system prepares | 0:40 |
| 6 | Follow-up scheduled; clock advanced (demo control) → reminder appears | No request dies in silence | 0:40 |
| 7 | Third request: ambiguous dates ("le week-end prochain") + "un petit geste sur le prix" → Orchestrator routes to human queue with reason | Safety layer, escalation, human decision | 1:00 |
| 8 | Staff resolves: sets dates, manager approves price → state moves to `quote_ready` | Human control is real, not decorative | 0:40 |
| 9 | Event log for one request: every transition, actor, timestamp | Traceability | 0:30 |
| 10 | Dashboard: status board (new / pending / needs human / confirmed) + KPI tiles labelled "Objectif pilote — à mesurer" | Manager view; honest KPIs | 0:45 |

Total ≈ 7:30. Cut steps 4 and 9 for a 5-minute version.

---

## 2. Demo scenarios (mock data, clearly labelled)

All names are fictional. Phone numbers are masked (`06 XX XX XX 01`).

### Scenario A — Standard, complete, available
> « Salam, je voudrais louer une citadine du 12 au 15 octobre, prise à l'agence de Rabat Agdal. C'est possible et c'est combien ? »

Expected: intent `quote`, confidence ≥ 0.9, category `citadine`, dates parsed, vehicle `CIT-03` available, draft quote with rate from table, follow-up scheduled +24 h.

### Scenario B — Unavailable → alternative
> « Bonjour, un SUV automatique du 20 au 27 octobre, retour aéroport Rabat-Salé svp. »

Expected: `SUV-01` on maintenance hold until 22/10, `SUV-02` booked → alternatives: `SUV-02` from 23/10 (shifted dates, if rule allows) **or** `BER-02` (berline automatique) same dates; reasons listed; draft proposes both politely.

### Scenario C — Ambiguous + sensitive → human
> « Slt, dispo une voiture pour le week-end prochain ? On est des clients réguliers, un petit geste sur le prix serait apprécié 🙏 »

Expected: dates ambiguous (`confidence 0.55`), no category, discount keyword → Orchestrator → `needs_human` (reason: dates ambiguës) **and** `escalated` flag (reason: remise demandée). Queue item shows context and suggested clarification question. Manager approves 10 % → state → `quote_ready`.

### Scenario D — Complaint (optional, if time)
> « La voiture de la semaine dernière avait un problème de clim et personne ne répond. »

Expected: intent `complaint` → immediate `escalated`, priority high, no draft generated automatically, manager notified in queue.

### Scenario E — Stalled lead (time-travel)
Scenario A after +48 h with no customer reply → `stalled`, Follow-up Agent recommends `call`, reminder draft ready.

---

## 3. Mock data files

```
demo/data/
  fleet.csv            # 8 vehicles: id, category, model, transmission, location, status, maintenance_until, daily_rate
  bookings.csv         # 6 existing bookings creating realistic conflicts
  rules.json           # min_days=1, max_days=30, buffer_hours=4, category_fallbacks, auto_confirm=false
  messages/            # scenario_a.txt … scenario_e.txt (French / light Darija)
  customers.csv        # 4 fictional customers, one flagged is_vip=true
```

`fleet.csv` sample:

| vehicle_id | category | model | transmission | location | status | maintenance_until | daily_rate_mad |
|---|---|---|---|---|---|---|---|
| CIT-01 | citadine | Dacia Sandero | manuelle | Agdal | active | | 250 |
| CIT-03 | citadine | Hyundai i10 | manuelle | Agdal | active | | 230 |
| BER-02 | berline | Peugeot 308 | automatique | Agdal | active | | 400 |
| SUV-01 | suv | Dacia Duster | automatique | Agdal | maintenance | 2026-10-22 | 450 |
| SUV-02 | suv | Hyundai Tucson | automatique | Hay Riad | active | | 550 |

---

## 4. Demo controls (hidden panel in Streamlit sidebar)

- **Reset demo** — wipes DB, reloads mock data.
- **Load scenario A/B/C/D/E** — pastes the message.
- **Advance clock +24 h / +48 h** — triggers follow-up sweep without waiting.
- **Toggle LLM / rules-only** — proves the system runs without external calls.
- **Show event log** — for any request.

---

## 5. Streamlit dashboard layout (pilot)

```
┌──────────────────────────────────────────────────────────────────────┐
│ ▌Données de démonstration — aucun client réel                        │
├────────────────────┬─────────────────────────────────────────────────┤
│ Nouvelle demande   │ File d'attente                                  │
│ [textarea]         │  ● À valider (2)   ● En attente client (3)      │
│ [Analyser]         │  ● Nouvelles (1)   ● Confirmées (4)             │
├────────────────────┴─────────────────────────────────────────────────┤
│ Demande #A-0012 · État : quote_ready                                 │
│  Structurée │ Disponibilité │ Brouillon │ Relance │ Journal          │
├──────────────────────────────────────────────────────────────────────┤
│ Indicateurs — Objectif pilote (à mesurer)                            │
│  1re réponse: — │ Délai: — │ Complètes: — │ Relances: — │ Escaladés: —│
└──────────────────────────────────────────────────────────────────────┘
```

KPI tiles in demo display **counts from demo events only** (e.g., "3 demandes, 1 escaladée") and never a percentage improvement.

---

## 6. Pre-demo checklist

- [ ] Runs offline with `rules-only` mode.
- [ ] All five scenarios produce the expected state in < 5 s each.
- [ ] Banner visible on every page.
- [ ] No real name, plate or phone number anywhere.
- [ ] Event log readable by a non-technical viewer (French labels).
- [ ] Laptop battery, screen mirroring, backup screenshots of each step (in case of failure).
- [ ] One-sentence answer ready for "what if it's wrong?": *« Il le dit, et il transmet à une personne. »*

---

## 7. What the demo must not do

- Send anything to a real channel.
- Show a "success rate" or "time saved" figure.
- Use the words "autonomous", "AI-powered", "revolutionary".
- Hide the human queue: it is the centrepiece, not an edge case.

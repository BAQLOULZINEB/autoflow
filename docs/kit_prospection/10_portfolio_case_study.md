# Case Study — Supervised Request Workflow for a Car Rental Agency (Rabat)

**Role:** AI Engineer & Automation Architect · **Format:** portfolio case study
**Status legend:** 🟦 hypothesis (pre-audit) · 🟩 measured · ⬜ to be filled after pilot

> Ingénieur IA & Architecte d'automatisation — j'identifie les frictions opérationnelles des entreprises et je les transforme en workflows intelligents, systèmes multi-agents et outils d'aide à la décision simples à déployer.

---

## 1. Struggle I found

A small car rental agency receives customer requests through WhatsApp, phone calls, Facebook, a web form and walk-ins. Each request needs the same things: dates, vehicle category, location, a price — and an availability check against a fleet table that lives in a spreadsheet.

What I observed (🟦 hypothesis until Phase 1; ⬜ replace with audit facts):

- Staff re-type customer details across channels and tools.
- Availability is checked by opening a spreadsheet and sometimes calling a colleague.
- The same questions (deposit, mileage, delivery) are answered by hand, every time.
- Quotes go out; when the customer goes quiet, follow-up depends on memory.
- "Where are we on this request?" is answered by scrolling through messages.

None of this is incompetence. It is what happens when capable people work fast across five tools that don't talk to each other. The cost is invisible: minutes per request, quotes lost in silence, and a manager who pilots by instinct.

**Baseline collected during audit:** ⬜ *(first-response time, time per request, % complete requests, follow-up rate — see §5)*

---

## 2. Architecture I designed

The owner's real question was never "can AI do this?" but "will I still be in control, and will it be reliable?" So the architecture is deliberately compact and supervised:

```
Customer request
   → Intake Agent          understands & structures; reports what's missing
   → Orchestrator          state · rules · validation · log · retries · escalation
   → Availability Agent    deterministic check on fleet + rules; proposes alternatives
   → Orchestrator
   → Follow-up Agent       drafts reply · schedules reminder · flags stalled leads
   → Human validation      pricing · complaints · ambiguity · final confirmation
   → Dashboard             status board + KPIs computed from events
```

Design decisions that matter:

| Decision | Why |
|---|---|
| **The orchestrator is the product.** | It owns a 10-state machine, an append-only event log, a rule engine, retry/escalation logic and the human queue. That is where reliability and measurability live. |
| **Three narrow agents, not "a multi-agent system".** | Each agent has one input contract, one output contract, and testable failure modes. |
| **Availability has no LLM.** | A rental system must never invent a free car. Deterministic rules + timestamped fleet snapshot. |
| **The system prepares; people commit.** | In the pilot, nothing is sent to a customer without a staff member. Escalation is a feature. |
| **Extraction must cite evidence.** | Every extracted field points to a text span or is `null`. Low confidence → human. |
| **Runs offline, rules-only, on a laptop.** | Adoption and privacy before sophistication. |

Full specification: [03_solution_architecture_en.md](03_solution_architecture_en.md).

---

## 3. System I built

⬜ *To be completed after Phase 3. Structure prepared below.*

**Stack:** Python · explicit state machine (or LangGraph if it simplified branching — decision recorded) · SQLite · Streamlit · optional LLM for extraction/drafting with regex fallback.

**What a user sees:**
1. Pastes a WhatsApp message → structured card with confidence and missing fields.
2. Availability result with reasons; alternative when the requested vehicle is unavailable.
3. A French draft reply to review, edit and send.
4. A reminder that appears when the customer goes silent.
5. A human queue where ambiguous dates or a discount request land — with context and a suggested action.
6. A manager board: new / pending / needs human / confirmed, and KPI tiles computed from the event log.

**Engineering evidence:**
- ⬜ transition-table tests (legal/illegal), crash-replay test, orphan-request check
- ⬜ scenario tests A–E end-to-end
- ⬜ extraction accuracy on N labelled messages (precision per field, honestly reported)
- ⬜ 100 % of escalation triggers verified to route to a human

Demo plan: [08_demo_plan.md](08_demo_plan.md).

---

## 4. Value created

Value is described in the owner's language and measured, not asserted.

| Business outcome | Mechanism | Evidence |
|---|---|---|
| Faster first replies | Structured request + draft ready | 🟩/⬜ first-response time before vs after |
| Fewer silent quotes | Scheduled reminders + stalled-lead detection | 🟩/⬜ follow-up rate, stalled leads surfaced |
| Less repetitive work | Extraction, availability, drafting prepared | 🟩/⬜ staff minutes per request |
| Complete requests earlier | Missing-field detection + clarification | 🟩/⬜ % complete at first pass |
| Manager visibility | Status board from events | Qualitative: owner can answer "where are we?" without asking |
| Team stays in control | Human queue, no autonomous send | 🟩/⬜ escalation count and resolution time — reported as a feature |

---

## 5. KPI section — transparent

| KPI | Baseline (Avant) | Pilot target (Objectif) | Observed (Après, mesuré) | Method / notes |
|---|---|---|---|---|
| First-response time | ⬜ | ⬜ | ⬜ | Timestamp received → first reply logged; ≥ 5 samples each period |
| Request handling time (to quote) | ⬜ | ⬜ | ⬜ | received → `quote_ready` |
| % requests complete at first pass | ⬜ | ⬜ | ⬜ | `missing_fields = []` on first intake |
| Follow-up rate (quotes with ≥ 1 reminder when silent) | ⬜ | ⬜ | ⬜ | `follow_ups.status = done` / eligible |
| Cases escalated to a human | ⬜ | n/a (not minimised) | ⬜ | `reviews` count by reason — a control feature |
| Staff manual minutes per request | ⬜ | ⬜ | ⬜ | Stopwatch sampling, same protocol both periods |
| Confirmed bookings / qualified leads | ⬜ | ⬜ | ⬜ | Only if the agency shares outcome data |

### Limitations (written before results)

- Small sample: a 2–4 week pilot in one agency yields ranges, not statistically strong estimates.
- Observation effect: staff may behave differently when measured; noted for both periods.
- Seasonality: rental demand varies; before/after windows should be comparable.
- Scope: pilot excludes voice, real channel integration and payment; results speak only to the request-to-quote workflow.
- Attribution: some gains may come from simply having a status board, not from agents; the event log allows separating these.

---

## 6. What I would do next

- Integrate one real channel (WhatsApp Business) behind the same human-send rule.
- Add SLA views for the manager (requests older than X hours).
- Extend rules from config to an owner-editable screen.
- Only if the audit proves demand: pricing suggestions with manager approval.

---

## 7. One-line summary for CV / LinkedIn

> Designed and built a supervised multi-agent workflow (intake, availability, follow-up + orchestrator with explicit state machine and human escalation) for a car rental agency in Rabat; measured before/after on first-response time, follow-up rate and manual time per request. *(⬜ numbers added only once measured.)*

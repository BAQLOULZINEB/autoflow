# 09 — Execution Plan

**Principle:** business-facing material first, code last. No agent is written before the workflow state machine and mock data exist. No KPI is claimed before a baseline is measured.

---

## Phase 0 — Preparation & audit hypotheses

| | |
|---|---|
| **Objective** | Enter the market with insight: a credible hypothesis, a proposal kit, and a clear ask. |
| **Outputs** | Docs 01–07 + visuals A–F; prospect shortlist (3–5 agencies in Rabat); personalised outreach per agency. |
| **Risks** | Generic outreach ignored; over-promising in materials; visuals look "AI-template". |
| **Validation** | Peer review of the one-pager by 2 non-technical readers (30-second comprehension test); every claim in docs tagged hypothesis or measurement plan. |
| **Deliverables** | This kit; outreach sent; first meeting booked. |
| **Exit criterion** | At least one 30-minute discovery meeting scheduled. |

## Phase 1 — Discovery & baseline KPI collection

| | |
|---|---|
| **Objective** | Replace hypotheses with observed facts and a numeric baseline. |
| **Outputs** | Completed audit template (doc 02); baseline table: first-response time (≥ 5 samples), time per request, % complete requests, follow-up rate estimate, escalation types; list of business rules; data availability decision (real anonymised vs mock). |
| **Risks** | No site access → fall back to interview-only baseline, labelled as estimates. Staff feel evaluated → framing script (doc 07 §3). Rules undocumented → capture as "règles non écrites" with owner sign-off. |
| **Validation** | Baseline reviewed and initialled by the owner; audit synthesis (doc 02 §5) agreed in a 15-minute readback. |
| **Deliverables** | `audit/baseline.md`, `audit/rules_v0.json`, updated docs 01 & 04 with observed facts (still no results claimed). |
| **Exit criterion** | Pilot workflow chosen; human-validation list confirmed by the owner. |

## Phase 2 — Prototype data & workflow state machine

| | |
|---|---|
| **Objective** | Build the skeleton that makes the system reliable: data model, states, transitions, event log — before any agent intelligence. |
| **Outputs** | SQLite schema (doc 03 §8); `rules.json`; mock fleet/bookings/messages (doc 08 §3); state machine with transition table and tests; event logging; consistency check ("no orphan requests"). |
| **Risks** | Over-engineering (LangGraph before need) → decision rule doc 03 §11. State explosion → cap at the 10 states defined. |
| **Validation** | Unit tests: every legal transition and every illegal transition; replay test after simulated crash; orphan check passes on 50 random-walk requests. |
| **Deliverables** | `src/core/{models,state_machine,events,rules}.py`, `tests/test_state_machine.py`, `demo/data/*`. |
| **Exit criterion** | A request can be moved through all states manually via CLI with a full event trail. |

## Phase 3 — Agents + dashboard

| | |
|---|---|
| **Objective** | Add the three agents and the human queue; ship the Streamlit dashboard. |
| **Outputs** | Intake Agent (LLM + regex fallback, evidence spans, confidence); Availability Agent (deterministic, no LLM); Follow-up Agent (drafts, reminders, next action); Orchestrator wiring (routing, validation, retries, escalation matrix doc 03 §4); Streamlit: new request, queue, request detail with tabs, event log, KPI placeholders; demo controls. |
| **Risks** | Hallucinated fields → evidence-span requirement + tests on 20 messages. Bad Darija/French handling → fallback to `needs_human`, measured. LLM cost/latency → rules-only switch. |
| **Validation** | Scenario tests A–E (doc 08 §2) pass end-to-end; extraction accuracy on a labelled set of 20–30 messages reported honestly (precision per field); 100 % of escalation-matrix triggers route to human in tests. |
| **Deliverables** | `src/agents/*`, `src/orchestrator.py`, `app/dashboard.py`, `tests/test_scenarios.py`, extraction accuracy report. |
| **Exit criterion** | Demo checklist (doc 08 §6) fully green, offline. |

## Phase 4 — Controlled demo & feedback

| | |
|---|---|
| **Objective** | Show the system to the owner and staff; collect concrete objections and adaptation needs. |
| **Outputs** | Demo session (doc 08); feedback log (what was unclear, what was wrong, what they'd change); prioritised adjustment list; go/no-go for a live pilot window. |
| **Risks** | Demo failure → backup screenshots; staff scepticism → run scenario C (human control) early; owner asks for out-of-scope features → log as future scope, don't build. |
| **Validation** | Owner can explain the workflow back in their own words; at least one staff member tries the queue live. |
| **Deliverables** | `feedback/demo_YYYY-MM-DD.md`, adjusted rules and drafts tone, v0.2 build. |
| **Exit criterion** | Written agreement (even a WhatsApp message) on pilot window, data handling, and who validates what. |

## Phase 5 — Pilot measurement & iteration

| | |
|---|---|
| **Objective** | Measure honestly over 2–4 weeks of supervised use; decide continue / adjust / stop. |
| **Outputs** | KPI dashboard with real "Après" column; weekly 15-minute check-ins; issue log; final before/after table with limitations; owner decision. |
| **Risks** | Low usage → measure adoption itself as a KPI; data too small → report ranges, not point estimates; Hawthorne effect → note it in limitations. |
| **Validation** | Every KPI computed from event timestamps (auditable); baseline and after measured with the same method; limitations section written before results are shared. |
| **Deliverables** | `pilot/results.md` (baseline / target / observed / limitations), case study (doc 10) finalised, video (doc 11) produced, owner testimonial if offered. |
| **Exit criterion** | Owner decision recorded; portfolio case study published with transparent KPIs. |

---

## Timeline (indicative)

```
Wk 1     Phase 0  ████
Wk 2–3   Phase 1      ████████
Wk 3–4   Phase 2          ████████
Wk 4–6   Phase 3              ████████████
Wk 7     Phase 4                          ████
Wk 8–11  Phase 5                              ████████████████
```

## Definition of "credible enough"

- A jury can trace any request from message to dashboard through the event log.
- An owner can say "this is how my day works" when seeing visual B.
- A recruiter sees an orchestrator with explicit states, rules, retries and escalation — not a chatbot.
- Nobody, anywhere in the deliverables, finds an unmeasured number.

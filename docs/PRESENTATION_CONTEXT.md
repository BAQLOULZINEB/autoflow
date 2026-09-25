# AutoFlow Presentation Context

Use this file as the factual context for generating a presentation about AutoFlow. It is the source of truth for the problem, the system, the evidence, and the limits of the claims.

## 1. Project Identity

- **Name:** AutoFlow
- **Purpose:** supervised automation of business workflows
- **Use case:** car-rental agency in Rabat, with Agdal, Hay Riad, and Rabat-Sale airport sites
- **Project status:** demonstrable V1 with fictitious data
- **Audience:** AI engineering jury, professors, and a non-technical agency manager
- **Presentation target:** 12-15 minutes, followed by a 5-minute live demo and Q&A
- **Core promise:** the system prepares; a person decides and sends

## 2. Problem

The agency receives requests through WhatsApp, Facebook, Instagram, phone, forms, and the counter. The current workflow is fragmented and manual:

1. Requests are spread across multiple channels.
2. Availability is checked manually in a spreadsheet.
3. The team answers repetitive questions about price, deposit, mileage, and delivery.
4. Follow-ups after quotes are easy to forget.
5. Nobody has a reliable shared view of request status.
6. The manager has limited operational visibility.

These are audit hypotheses to validate on site, not measured business losses. The presentation must clearly distinguish observed facts, project assumptions, and future pilot measurements.

## 3. Central Problem Statement

How can a small business automate repetitive request handling without removing human responsibility, inventing availability, or hiding decisions inside a black box?

## 4. Solution

AutoFlow is a supervised workflow composed of:

- **One orchestrator:** LangGraph StateGraph, state routing, escalation, event journal, and human checkpoints.
- **Three specialized agents:**
  - Intake: structures the message and reports missing fields, evidence, and confidence.
  - Availability: deterministic SQL and date logic; no LLM; returns vehicles, alternatives, and readable reasons.
  - Follow-up: prepares French drafts, schedules reminders, and marks silent leads as stalled.
- **One human decision layer:** the team or manager approves, edits, rejects, completes, or closes each sensitive case.

## 5. Non-Negotiable Invariants

1. AutoFlow never sends a client message autonomously. A human click is required.
2. AutoFlow never invents availability. Availability is computed by deterministic code.
3. An extracted field without verbatim evidence in the original message is rejected.
4. Every state transition writes an auditable event with actor, reason, and timestamp.
5. KPI values are derived from the event journal, not manually declared.

## 6. Runtime Flow

```text
message or form
  -> intake extraction
  -> confidence and evidence gates
  -> deterministic availability check
  -> escalation matrix
  -> French draft and follow-up plan
  -> persistent human interrupt
  -> approve, edit, reject, complete, or close
  -> event journal and KPI aggregation
```

The workflow uses ten business states: `new`, `incomplete`, `checked`, `quote_ready`, `pending_customer`, `stalled`, `needs_human`, `escalated`, `confirmed`, and `closed`.

## 7. Architecture and Stack

- Frontend: React 19, Vite, TypeScript
- Backend: FastAPI, Python
- Orchestration: LangGraph with `interrupt()` and `Command`
- Persistence: SQLAlchemy, SQLite locally, PostgreSQL as a deployment option
- Integrations: n8n at the edge for webhooks and notifications
- LLM: optional Anthropic, OpenAI, or Ollama; the default mode runs offline with rules
- Deployment options: laptop demo, Docker cloud deployment, or static frontend plus Python backend

## 8. Verified Evaluation Results

These values are verified in the project documentation and may be used as current results:

| Measure | Verified value | Evidence or qualification |
|---|---:|---|
| Automated tests | 16 passing | 8 end-to-end workflow tests plus 7 simulations and a catalogue test |
| Intake pickup-date accuracy | 89% | 39/44 labeled examples |
| Intake return-date accuracy | 82% | 36/44 labeled examples |
| Intake vehicle-category accuracy | 91% | 40/44 labeled examples |
| Intake intention accuracy | 100% | 45/45 labeled examples |
| Incorrect extractions routed to human review | 100% | 8/8 incorrect extractions were caught |
| Calibration at confidence >= 0.8 | 94% fully correct | On the current generated evaluation set |
| Calibration below 0.8 | 0% fully correct | Low-confidence cases are intentionally escalated |
| Replayed history | 45 requests, about 370 events | Generated demo data, not production activity |

## 9. What Must Not Be Claimed

Do not claim measured business gains for response time, conversion, revenue, saved minutes, or customer satisfaction. Those values are unknown until a real before/after pilot.

Always disclose these limitations:

- The dataset is fictitious.
- The evaluation messages and labels come from the same generator, so results may be optimistic.
- Real messages in French, Darija, and ambiguous date expressions require a hand-labeled pilot dataset.
- The WhatsApp Business connector is future work; n8n currently notifies and forwards data, but does not autonomously send client messages.
- The displayed activity counts are simulated demo counters, not business gains.

## 10. Pilot Metrics to Measure Later

The presentation may show these as a measurement plan, never as current results:

- time to first response
- time to quote readiness
- percentage of requests complete on first message
- follow-up completion rate
- manual minutes per request
- percentage of escalated cases

Use the same definitions before and after the pilot. Report ranges for samples smaller than 30 and distinguish time saved from work moved to human review.

## 11. Demonstrable Experiments

The live or interactive presentation should include these experiments:

1. Standard request: complete dates and category produce a quote draft.
2. Unavailable vehicle: the deterministic checker returns alternatives and reasons.
3. Ambiguous dates plus discount: the system asks for clarification, then escalates to the manager.
4. Complaint: the request goes directly to human escalation without a quote draft.
5. Time travel: `+24 h` creates a reminder; `+72 h` moves a silent lead to `stalled`.
6. Failure mode: remove or disable the LLM and show that rules still process the request.
7. Evidence gate: provide an unsupported field and show that it is rejected.

## 12. Narrative

Use this sequence:

```text
operational chaos
  -> precise problem
  -> supervised design choice
  -> architecture and workflow
  -> evaluation and failure behavior
  -> live experiments
  -> honest pilot roadmap
```

The speaker should sound like an engineer who diagnosed a workflow, made explicit trade-offs, built a working system, measured what was possible, and refuses to overclaim what has not yet been measured.

## 13. Source Files

- Current slide content: `docs/PRESENTATION.md`
- Project source of truth: `docs/00-CONTEXTE.md`
- Architecture views: `docs/02-architecture.md`
- Evaluation details: `docs/05-evaluation.md`
- Live demo and deployment guidance: `docs/04-demo-et-deploiement.md`
- Workflow diagram: `docs/diagrams/03-workflow.html`
- Existing frontend: `frontend/`

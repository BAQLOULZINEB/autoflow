# CONTEXT.md — Professional Positioning and Project Context

## Who I am becoming
I am positioning myself as an **AI Engineer & Automation Architect**.

My professional value is not “I use LangChain” or “I build chatbots.”
My value is the ability to:
1. identify operational friction inside a business,
2. design a simple and reliable workflow architecture,
3. build a working prototype,
4. translate technical work into clear business value.

## Positioning statement
> **Ingénieur IA & Architecte d’automatisation — j’identifie les frictions opérationnelles des entreprises et je les transforme en workflows intelligents, systèmes multi-agents et outils d’aide à la décision simples à déployer.**

## Four-layer identity
- **Detective**: audit real work, identify repetitive work, delays, forgotten follow-ups, unclear ownership, and error-prone handoffs.
- **Architect**: design workflows, specialized agents, middleware/orchestration, escalation rules, human approval points, and measurement.
- **Builder**: ship a credible working demo, not slideware.
- **Translator**: make business value obvious to a non-technical owner in 30 seconds.

## Current flagship case
**Business:** car rental agency in Rabat, Morocco.

**Internship title:**
> Projet de stage – Architecture d’un système multi-agents pour l’automatisation des workflows opérationnels d’une agence de mobilité.

**Plain-language version for a manager:**
> Mise en place d’un système intelligent pour automatiser le traitement des demandes clients, le suivi des réservations et la coordination opérationnelle d’une agence.

## Business problem hypothesis
A car rental agency can lose time and revenue through:
- requests arriving through WhatsApp, phone, Facebook, forms, or walk-ins,
- manual copying of client details,
- slow or inconsistent availability checking,
- missed follow-ups after a quote,
- employees repeatedly answering the same questions,
- unclear status of leads, reservations, and pending actions,
- manager visibility relying on messages and memory rather than a clean view.

Do not claim these are confirmed facts. Present them as hypotheses to validate during an audit.

## Solution promise
The system should reduce repetitive manual work, speed up responses, improve follow-up discipline, and provide a simple operational view while keeping humans responsible for final exceptions and sensitive decisions.

The system is a **supervised workflow**, not an autonomous replacement for employees.

## Mandatory architecture
Keep the architecture compact: **1 orchestrator + 3 specialized agents + human-in-the-loop**.

### 1. Intake Agent
**Purpose:** capture and structure an incoming request.

**Inputs:** WhatsApp/form/manual entry, customer message, preferred dates, vehicle type, pickup/return location, budget, customer profile if known.

**Responsibilities:**
- detect customer intent: information request, quote, reservation, modification, complaint;
- extract dates, vehicle category, location, and constraints;
- ask for missing information using a short, natural response;
- normalize the request into a structured record;
- send the request to the orchestrator.

**Output:** structured request + confidence + missing fields.

### 2. Availability Agent
**Purpose:** validate feasibility and propose useful alternatives.

**Inputs:** structured request, availability table/database, fleet constraints, rental rules.

**Responsibilities:**
- check vehicle availability for requested dates;
- apply basic rules: booking duration, category, location, status, maintenance hold;
- select matching vehicles;
- propose alternatives if the requested vehicle is unavailable;
- return an explainable result, never inventing availability.

**Output:** available options / alternatives / reason for no availability.

### 3. Follow-up Agent
**Purpose:** ensure the request does not disappear after a quote or response.

**Inputs:** quote/status, timestamp, customer response state, follow-up policy.

**Responsibilities:**
- draft customer-friendly replies;
- schedule a reminder if no response occurs;
- detect stalled leads;
- suggest next best action: respond, follow up, call, escalate, close;
- log every action for the dashboard.

**Output:** draft message + action recommendation + follow-up status.

### 4. Orchestrator / Middleware
**Purpose:** coordinate the workflow and protect operational reliability.

**Responsibilities:**
- route tasks between agents;
- keep a state record: new, incomplete, checked, quote-ready, pending customer, confirmed, escalated, closed;
- validate agent outputs;
- handle retries and failures;
- log decisions and actions;
- enforce business rules;
- route low-confidence, ambiguous, exceptional, or sensitive cases to a human.

**Important:** the orchestrator is the differentiator. It proves workflow architecture skills, not just chatbot building.

### 5. Human-in-the-loop
A staff member validates or handles:
- low-confidence extractions,
- unclear dates or identity,
- special prices or discounts,
- unavailable vehicles with sensitive customers,
- complaints,
- final confirmation when company policy requires it.

## Workflow to demonstrate
Customer request → Intake Agent → Orchestrator → Availability Agent → Orchestrator → customer response/quote draft → Follow-up Agent → human validation when required → status dashboard.

## Do not over-engineer
This is a credible pilot, not a full reservation ERP.
Do not add unnecessary agents, complex autonomous actions, predictive maintenance, dynamic pricing, voice systems, or external integrations unless the business audit proves they are necessary.

A simple stack is enough:
- Python
- Streamlit dashboard
- CSV or SQLite/PostgreSQL prototype data
- LangGraph or a clean state-machine workflow
- optional LLM for extraction and response drafting
- manual mock data if real data is unavailable

## Storytelling framework
Every deliverable must tell the same 4-part story:
1. **Struggle I found** — a real workflow pain or audit hypothesis.
2. **Architecture I designed** — workflow, agents, orchestration, human control.
3. **System I built** — concrete demo and user-facing behavior.
4. **Value created** — time, response speed, follow-up quality, exceptions, and business outcomes.

The expanded narrative is:
> Struggle → Workflow → Agents → Supervision → KPI before/after

## KPIs to measure honestly
Never invent savings. Use baseline measurements, estimates clearly labeled as estimates, or demo scenario results.

Track:
- first-response time;
- quote turnaround time;
- number/rate of missed follow-ups;
- percentage of requests with complete information;
- number of manual handoffs;
- number/rate of human exceptions;
- employee minutes spent per request;
- completed bookings or qualified leads, if real data allows it.

## Portfolio format
For this and every future project, prepare:
- one-page visual: **Problem → System → Result**;
- a simple workflow diagram;
- a simple agent-role diagram;
- a before/after KPI table;
- 60-second demo video showing an employee day before and after;
- short business story in French, technical architecture in English if useful.

## Tone and market fit
The agency owner buys clarity, time savings, reliability, and better follow-up — not a list of frameworks.

Customer-facing documents should be:
- French-first;
- concise, confident, respectful;
- easy to understand for a Moroccan SME owner;
- optionally Darija-friendly in spoken pitch, without forcing it into formal documents.

Never sound needy. The posture is: “I studied a likely operational issue and prepared a focused pilot that can validate its value.”

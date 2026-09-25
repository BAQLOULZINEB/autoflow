# AutoFlow - Ultimate PowerPoint Generation Prompt

> Copy this entire file into a PowerPoint-capable AI assistant. Attach the following source files with it: `docs/rapport.pdf`, `docs/00-CONTEXTE.md`, `docs/02-architecture.md`, `docs/05-evaluation.md`, `docs/PRESENTATION.md`, and screenshots or a live URL of the current AutoFlow site.

```text
You are an expert academic presentation designer, AI systems architect, technical storyteller, and PowerPoint engineer.

Create a complete, polished, academic PowerPoint presentation for the project AutoFlow. The deck is for a final internship defense before an AI engineering jury, professors, and a non-technical business manager.

The presentation must make the audience understand five things:

1. The real operational problem.
2. Why the project uses supervised automation instead of an autonomous chatbot.
3. How the architecture works technically and operationally.
4. What was actually built and what the evidence shows.
5. What remains to be measured in a real pilot.

The presentation must feel like an engineer presenting a working system, not like a generic AI marketing deck or a student reading a report.

======================================================================
SOURCE MATERIAL AND EVIDENCE POLICY
======================================================================

Use these sources in this order:

1. `docs/00-CONTEXTE.md`: project source of truth and verified terminology.
2. `docs/rapport.pdf`: academic report, methodology, architecture, implementation, evaluation, limitations, and conclusions.
3. `docs/02-architecture.md`: architecture diagrams and runtime flow.
4. `docs/05-evaluation.md`: tests, metrics, robustness, and pilot measurement plan.
5. `docs/PRESENTATION.md`: existing narrative and demo sequence.
6. The current AutoFlow website or provided screenshots: only for authentic interface visuals and current UI state.

Do not invent facts. Do not create fake customer logos, fake screenshots, fake production results, fake revenue, fake time savings, or fake deployment claims.

Classify claims internally using these labels:

- FACT: implemented or reproducible in the repository.
- TECHNICAL RESULT: measured by tests or the documented evaluation.
- SIMULATED: generated demo activity or synthetic dataset.
- AUDIT HYPOTHESIS: plausible business friction that still needs field validation.
- PILOT TO MEASURE: future business KPI with no current value.
- LIMITATION: known boundary of the current V1.

If a source conflict exists, choose the most cautious version and mention the conflict in speaker notes. Never turn a simulated count into a business result.

The following statements are mandatory:

- The data is fictitious and controlled.
- AutoFlow does not claim business gains before a real pilot.
- The evaluation dataset is limited and may be optimistic because messages and labels were generated together.
- The project prepares recommendations; a human decides and sends.
- The system never autonomously sends a client message.
- Availability is deterministic and does not come from an LLM.

======================================================================
PROJECT CONTEXT
======================================================================

Project: AutoFlow - intelligent automation of business workflows.

Academic context: AI Engineer internship project in Artificial Intelligence and Data Science at EMSI Rabat.

Business case: a car-rental agency in Rabat with Agdal, Hay Riad, and Rabat-Sale airport locations.

Business problem: requests arrive through WhatsApp, Facebook, Instagram, phone, forms, and the counter. The team manually re-enters information, checks availability in a spreadsheet, answers repetitive questions, forgets follow-ups, loses track of request ownership, and lacks a reliable manager view.

Central research and engineering question:

How can a service SME automate customer-request handling without removing human responsibility, inventing information, or hiding decisions inside a black box, while proving that the result is reliable, explainable, and measurable?

Solution principle:

    The system prepares. The team decides.

Architecture:

- One LangGraph orchestrator.
- Three specialized agents.
- One mandatory human decision layer.
- One auditable event journal.

Agent responsibilities:

- Intake - understand: extracts structured fields, missing information, evidence, confidence, and typed signals.
- Availability - verify: checks dates, bookings, maintenance, buffers, and alternatives deterministically; no LLM.
- Follow-up - prepare: creates French drafts, injects prices from the vehicle table, schedules reminders, and marks silent leads as stalled.

Three invariants:

1. No client message is sent without a human click.
2. No availability or field is invented. Unsupported LLM fields are rejected by the evidence gate.
3. Every transition is logged with actor, reason, and timestamp.

Technical stack:

- Python, FastAPI, Pydantic.
- LangGraph StateGraph, `interrupt()`, `Command(resume)` and `Command(goto)`.
- SQLAlchemy with SQLite locally and PostgreSQL as a future deployment option.
- React 19, Vite, TypeScript.
- n8n as an edge webhook and notification layer, never as the decision core.
- Optional LLM provider: Anthropic, OpenAI, or Ollama. The rules-first mode runs offline.
- Docker Compose for local deployment; Vercel/Netlify plus Docker backend as deployment options.

Current V1 scope:

- 24 vehicles.
- 80 bookings.
- 40 customers.
- 45 historical requests replayed through the real graph.
- Approximately 370 generated events.
- Seven business simulations used as acceptance tests.
- Ten business states.
- Twenty-four API routes.
- Ten admin screens plus public intake and presentation mode.

======================================================================
VERIFIED RESULTS TO SHOW
======================================================================

Show each metric with its denominator, source, and limitation.

- 16 automated tests passing.
- Pickup-date accuracy: 89% (39/44).
- Return-date accuracy: 82% (36/44).
- Vehicle-category accuracy: 91% (40/44).
- Intention accuracy: 100% (45/45).
- Incorrect extractions routed to human review: 8/8 (100%) in the current sample.
- At confidence >= 0.8, fully correct extractions: 94% in the current generated evaluation set.
- At confidence < 0.8, fully correct extractions: 0% in that evaluation set.
- Simulated history replay: 45 requests and approximately 370 events.

When showing the 94% calibration result, state that the report also records 36/36 fully correct examples at confidence >= 0.8. Do not present calibration as a universal guarantee.

Never present these as already measured:

- response-time reduction;
- conversion improvement;
- revenue increase;
- customer satisfaction improvement;
- minutes saved per request;
- real-world availability accuracy.

Show these as pilot metrics to measure:

- time to first response;
- time to quote readiness;
- percentage of requests complete on the first message;
- follow-up completion rate;
- manual minutes per request;
- percentage of escalated cases.

======================================================================
MANDATORY VISUAL SYSTEM
======================================================================

Use this exact palette as the design system. Do not replace it with a default Microsoft theme.

:root {
  --navy: #103447;
  --text: #073452;
  --lime: #C7F64F;
  --mint: #A9E2D8;
  --peach: #FFD18A;
  --lavender: #D5C8F2;
  --ivory: #FFF9EF;
  --aqua: #96DCCB;
}

Color roles:

- Navy: primary background, dark diagrams, strong contrast panels.
- Text blue: body text on ivory and light slides.
- Lime: primary action, human checkpoint, success, active path, important highlights.
- Mint: stable system components, verified flow, neutral positive states.
- Peach: warning, ambiguity, escalation, pilot caveat.
- Lavender: optional technical layer, data, secondary architecture category.
- Ivory: main light background, readable academic content.
- Aqua: secondary accent, connector lines, information states.

Contrast rules:

- Use ivory text on navy.
- Use text blue on ivory, mint, peach, lavender, or aqua.
- Use navy text on lime.
- Never place small text directly on a saturated accent.
- Never use lime as a large body background.
- Never use more than three accent colors on one slide.

Typography:

- Titles: Manrope ExtraBold, or Aptos Display if Manrope is unavailable.
- Body: Aptos, Inter, or Source Sans 3.
- Code and state names: IBM Plex Mono or Aptos Mono.
- Use strong typography hierarchy, not excessive decoration.
- Do not use all caps for paragraphs.
- Keep body text large enough for a room: minimum 20 pt, preferably 24 pt.
- Use 30-42 pt slide titles and 48-72 pt hero numbers.

Visual character:

- Editorial engineering, calm, precise, human-centered.
- Ivory pages alternate with navy pages.
- Use lime as a visual signal for human control and validated transitions.
- Use asymmetric layouts, a visible grid, generous whitespace, and thin connector lines.
- Use rounded corners sparingly, maximum 12 px equivalent.
- Avoid card grids that make every slide look like a dashboard.
- Avoid generic stock photos. Prefer project UI screenshots, diagrams, message fragments, timelines, state machines, and evidence panels.
- Use real screenshots from the supplied site or clearly marked placeholders.
- Never fabricate an interface screenshot.

PowerPoint implementation:

- Use editable native shapes, text, tables, and connectors wherever possible.
- Do not flatten important diagrams into a single image.
- Group related objects logically and name groups meaningfully.
- Use Morph or Fade transitions only when they clarify flow.
- Use appear/wipe animations for progressive reasoning.
- Avoid bouncing, spinning, excessive zoom, and decorative animations.
- All information must remain understandable when animations are skipped.
- Provide speaker notes for every slide.

======================================================================
DECK FORMAT
======================================================================

Create a 16:9 widescreen PowerPoint deck in French.

Target duration: 15 minutes presentation, 5 minutes live demonstration, 5 minutes Q&A.

Create 18 slides total:

1. Cover and promise.
2. Executive summary: problem, solution, proof.
3. A morning inside the agency.
4. Six operational frictions.
5. Research problem and design constraints.
6. Why supervised automation instead of an autonomous agent.
7. AutoFlow at a glance: one orchestrator, three agents, one human.
8. Context architecture: actors, channels, and the human boundary.
9. Container architecture: frontend, API, graph, database, checkpointer, integrations.
10. End-to-end request flow.
11. LangGraph workflow: nodes, guards, interrupt, and resume.
12. The three agents and their safety boundaries.
13. Escalation matrix and state machine.
14. Admin product: queue, live trace, simulations, and presentation mode.
15. Evaluation protocol and verified metrics.
16. Robustness: what happens when the system fails.
17. Demonstration plan, pilot measurement, limitations, and next steps.
18. Conclusion and Q&A.

Optional appendix slides may be added after slide 18, clearly labeled APPENDIX:

- technical stack and decision records;
- API routes and data model;
- test-to-requirement coverage;
- detailed metric table;
- deployment topologies;
- bibliography and source documents.

======================================================================
SLIDE-BY-SLIDE CONTENT REQUIREMENTS
======================================================================

SLIDE 1 - COVER

Title: AutoFlow
Subtitle: Le système prépare. L'équipe décide.
Supporting line: Automatisation supervisée des workflows métier.
Case: Agence de location de voitures - Rabat.
Academic line: Projet de stage AI Engineer - EMSI Rabat.

Design: navy background, oversized title, lime underline, small mint/aqua system line. No dense content. Use a subtle thin workflow line in the background.

SLIDE 2 - EXECUTIVE SUMMARY

Show three columns:

- Problem: requests scattered across channels and manually coordinated.
- Solution: LangGraph workflow, three agents, human decision checkpoint.
- Proof: 16 tests, 8/8 observed extraction errors routed to human review, measured limits clearly declared.

Add an evidence legend: FACT, TECHNICAL RESULT, PILOT TO MEASURE.

SLIDE 3 - A MORNING INSIDE THE AGENCY

Create a cinematic horizontal timeline:

WhatsApp message -> client at counter -> spreadsheet check -> quote sent -> silence -> manager asks “On en est où ?”.

Make it clear that this is an audit reconstruction and operational narrative, not a statistical claim.

SLIDE 4 - SIX FRICTIONS

Show F1-F6 with a visual rhythm, not six identical cards:

- scattered requests;
- manual availability checks;
- repetitive questions;
- forgotten follow-ups;
- unclear ownership and status;
- limited manager visibility.

Label their cost as probable operational friction, not measured financial loss.

SLIDE 5 - CENTRAL PROBLEM

Display this question prominently:

How can a service SME automate customer requests without removing human responsibility, inventing information, or creating a black box?

Under it, show three constraints:

- no autonomous client messaging;
- no invented availability or fields;
- every decision explainable and measurable.

SLIDE 6 - THE ARCHITECTURAL COUNTER-CHOICE

Contrast two paths:

- Autonomous bot: fast-looking, opaque, risky, sends without a decision boundary.
- Supervised workflow: prepares, verifies, escalates, waits, resumes, logs.

Make the second path dominant in lime and mint. State: confidence is designed into the workflow, not promised by a model.

SLIDE 7 - AUTOFlow AT A GLANCE

Use a large central composition:

1 orchestrator + 3 specialized agents + 1 human decision layer.

Visual verbs:

- Intake = comprendre.
- Availability = vérifier.
- Follow-up = préparer.
- Human = décider.

Use a lime human checkpoint as the visual anchor.

SLIDE 8 - CONTEXT ARCHITECTURE

Show:

Client channels -> AutoFlow -> team and manager.

Place optional LLM, n8n, and future WhatsApp Business outside the core boundary using dotted lines. Make the boundary explicit: AutoFlow produces drafts; a person sends.

Use editable PowerPoint connectors and a legend for FACT versus FUTURE/AUDIT-GATED.

SLIDE 9 - CONTAINER ARCHITECTURE

Show these editable layers:

- React/Vite/TypeScript admin frontend.
- FastAPI/Pydantic API.
- LangGraph orchestrator.
- Intake, Availability, and Follow-up agents.
- Rules JSON.
- SQLite/PostgreSQL database.
- LangGraph SQLite checkpointer.
- n8n edge webhook and optional LLM.

Show that the frontend has no secret and that the LLM is optional.

SLIDE 10 - END-TO-END REQUEST FLOW

Animate one request through:

raw French or Darija message -> normalized structured request -> evidence and confidence gates -> deterministic availability -> escalation rules -> French draft -> human interrupt -> decision -> event journal and follow-up.

Reveal the evidence before revealing the confidence score. Show price injection from the fleet table, not generated price text.

SLIDE 11 - LANGGRAPH WORKFLOW

Create a readable state graph with these nodes:

START -> intake -> route_after_intake -> clarify/escalate/availability -> decide_after_availability -> sensitive/draft -> human_review -> finalize -> END.

Highlight:

- `interrupt()` pauses the graph.
- `Command(resume)` continues after a decision.
- `Command(goto=availability)` rechecks after missing fields are completed.
- SQLite checkpoint preserves pending validation after restart.

Use animation to light the nominal path, then branch to a human path.

SLIDE 12 - THREE AGENTS

Use three vertical zones, each with capability and boundary:

Intake:
- rules always run;
- optional LLM with evidence gate;
- confidence and typed signals.

Availability:
- SQL and date overlap;
- 4-hour buffer, maintenance, alternatives;
- zero LLM.

Follow-up:
- French templates;
- price injected from table;
- +24 h reminder, maximum two reminders, +72 h stalled.

SLIDE 13 - ESCALATION AND STATE MACHINE

Show a compact state machine and beside it the escalation triggers:

- complaint -> manager;
- missing fields or low confidence -> team;
- discount -> manager;
- more than 14 days or more than 6000 MAD -> manager;
- unavailable or invalid -> team;
- more than 8 hops -> human.

Make clear that `rules.json` is versioned and transitions are legal and journaled.

SLIDE 14 - ADMIN PRODUCT

Use authentic screenshots from the current site where available. If no screenshot is available, use labeled wireframe placeholders, never invented screenshots.

Show four surfaces:

- validation queue: who decides what and why;
- live trace: actual path and evaluated rules;
- simulations: seven playable business cases and acceptance tests;
- presentation mode: readable flow for defense.

Caption the live trace: reasoning is inspectable, not hidden.

SLIDE 15 - EVALUATION PROTOCOL AND METRICS

Use a three-level evaluation ladder:

1. Specification compliance: 16 automated tests passing.
2. Extraction quality: field-level accuracy and calibration on 45 labeled messages.
3. Business value: not yet measured; defined as a before/after pilot.

Render metric tiles with denominator and qualification:

- 39/44, 89% pickup date.
- 36/44, 82% return date.
- 40/44, 91% category.
- 45/45, 100% intention.
- 8/8, 100% observed incorrect extractions caught by human review.
- 94% fully correct at confidence >= 0.8 in the current generated set.

Keep “business impact: to measure” visually separate from technical evidence.

SLIDE 16 - ROBUSTNESS AND FAILURE BEHAVIOR

Use a failure -> response layout:

- LLM unavailable -> rules-only fallback, `llm_failed` flag, adjusted confidence.
- unsupported evidence -> field rejected, clarification requested.
- restart during review -> checkpoint restores pending interrupt.
- illegal transition -> HTTP 409, no write.
- loop over eight hops -> human escalation.
- too many reminders -> stalled state and call recommendation.

Make the human route the visual safety net, not an afterthought.

SLIDE 17 - DEMO, PILOT, AND NEXT STEPS

Divide the slide into three zones.

Demo sequence:

1. Load dashboard.
2. Run standard request.
3. Show live trace.
4. Run ambiguous dates plus discount.
5. Complete fields and observe second escalation.
6. Advance +24 h and +72 h.
7. Show simulation assertions.

Pilot plan:

- audit baseline;
- annotate at least 30 real messages;
- controlled LLM evaluation;
- 2-4 week before/after pilot.

Limitations:

- fictitious dataset;
- no business gain claimed;
- direct WhatsApp and payment excluded;
- real-data compliance to be framed with the agency.

SLIDE 18 - CONCLUSION AND Q&A

Use a calm navy ending with a lime final statement:

AutoFlow does not automate responsibility.
It organizes it, makes it explainable, and measures what it can prove.

Below it:

Built: a working supervised workflow.
Measured: technical behavior and extraction evidence.
Next: a real pilot with real baseline metrics.

End with “Merci - Questions ?”.

======================================================================
SPEAKER NOTES AND DEFENSE PREPARATION
======================================================================

For every slide, add speaker notes containing:

1. Main message in one sentence.
2. A natural 30-60 second script in French.
3. One transition sentence to the next slide.
4. One likely jury question.
5. A concise answer grounded in the report.
6. The evidence level and limitation.

Prepare explicit answers to these questions:

- Where is the AI if availability is deterministic?
- Why LangGraph instead of a home-made state machine?
- Why not let the LLM send the message?
- How does the evidence gate reject hallucinated fields?
- Why are the evaluation labels potentially optimistic?
- What does 8/8 actually prove, and what does it not prove?
- Why are business gains not shown?
- What happens if the LLM or database fails?
- Why n8n is at the edge and not the orchestration core?
- How would the architecture generalize to a clinic or artisan?
- What would be the first step of a real pilot?

Use this short defense answer when asked for the main contribution:

“La contribution principale n'est pas un modèle nouveau. C'est une discipline d'architecture : les agents proposent, l'orchestrateur route selon des règles versionnées, l'humain décide, tout est tracé, et aucun gain métier n'est annoncé avant d'être mesuré.”

======================================================================
ANIMATION AND INTERACTION PLAN
======================================================================

Use animations as controlled experiments:

- Slide 3: reveal the operational timeline step by step.
- Slide 7: reveal 1, then 3, then 1.
- Slide 10: reveal evidence before confidence and routing.
- Slide 11: animate the request path and pause at human review.
- Slide 13: animate one escalation trigger at a time.
- Slide 15: reveal denominator, then percentage, then limitation.
- Slide 16: animate failure input into a safe human route.
- Slide 17: animate +24 h and +72 h as a time axis.

Never make the presentation depend on animation to understand the content.
Use only Fade, Wipe, Morph, and simple emphasis. Keep transitions under 500 ms.

======================================================================
POWERPOINT QUALITY REQUIREMENTS
======================================================================

Deliver:

- an editable `.pptx` file;
- a PDF export;
- a speaker-notes version;
- a one-page references and evidence appendix;
- a final QA checklist.

The PowerPoint must pass these checks:

- 16:9 widescreen format;
- all text readable at 100% zoom;
- no overlapping elements;
- no clipped labels in diagrams;
- every diagram remains legible when printed;
- all numbers show denominator and source qualification;
- all screenshots are authentic or explicitly marked placeholders;
- no unsupported business result appears;
- the human decision boundary is visible in at least five slides;
- every external or future integration is labeled as optional, future, or audit-gated;
- animations can be skipped without losing meaning;
- slides 1, 7, 11, 15, 16, and 18 remain understandable when viewed alone;
- notes are present for every slide;
- sources are listed in the appendix.

Before returning the presentation, perform a content audit and report:

FACTS USED
TECHNICAL RESULTS USED
SIMULATED CONTENT SHOWN
AUDIT HYPOTHESES SHOWN
PILOT METRICS RESERVED FOR FUTURE MEASUREMENT
LIMITATIONS DISCLOSED
AUTHENTIC ASSETS USED
PLACEHOLDERS STILL NEEDED
OPEN QUESTIONS FOR THE AUTHOR

Do not return a generic outline. Return the complete presentation with slide content, visual layout, speaker notes, animation plan, sources, and QA report.
```

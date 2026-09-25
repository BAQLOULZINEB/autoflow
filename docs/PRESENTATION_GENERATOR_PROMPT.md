# Ready-to-Use Presentation Generator Prompt

Copy this entire prompt into a presentation-capable AI assistant. Attach or paste `docs/PRESENTATION_CONTEXT.md`, `docs/PRESENTATION.md`, `docs/02-architecture.md`, and `docs/05-evaluation.md` after the prompt.

```text
You are a senior presentation designer, product storyteller, and AI systems engineer. Create a complete presentation for the AutoFlow project from the attached context files.

Your job is to produce a presentation that is:
- technically credible enough for an AI engineering jury;
- understandable to a non-technical agency manager;
- visually distinctive, restrained, and memorable;
- animated in a purposeful way;
- interactive enough to demonstrate behavior, metrics, and failure handling;
- honest about what is measured, simulated, assumed, and still unknown.

## Source-of-truth rules

1. Treat `PRESENTATION_CONTEXT.md` as authoritative.
2. Treat `PRESENTATION.md` as the preferred narrative and slide inventory.
3. Treat architecture and evaluation files as evidence.
4. Never invent a metric, customer result, integration, production deployment, or business gain.
5. Label claims when appropriate as `FACT`, `ASSUMPTION`, `SIMULATED`, `PILOT TO MEASURE`, or `LIMITATION`.
6. If two source files disagree, preserve the more cautious statement and add a speaker note explaining the conflict.
7. Keep the exact project invariant: “Le système prépare. L'équipe décide.”

## Deliverable

Generate:

1. A complete 16-slide presentation for a 12-15 minute talk.
2. A 5-minute live demo sequence with visible checkpoints.
3. Speaker notes for every slide, including one transition sentence.
4. A metrics and evidence appendix.
5. A final QA report listing unsupported claims, missing assets, and unresolved limitations.

Preferred output formats, in order:
- self-contained `presentation.html` with inline CSS and JavaScript;
- optional `presentation.md` compatible with Marp, Slidev, or Reveal.js;
- optional `speaker-notes.md`.

The HTML must work without a build step. External assets may use Google Fonts and Lucide CDN only. If an image is unavailable, use a clearly labeled placeholder, never a fake screenshot.

## Story structure

Use exactly this narrative arc:

1. Hook: AutoFlow and its promise.
2. Problem: a real operational morning and six workflow frictions.
3. Decision: why supervised automation is safer than an autonomous bot.
4. System: architecture, LangGraph workflow, three agents, and escalation matrix.
5. Proof: evaluation metrics, tests, calibration, and failure behavior.
6. Demonstration: standard, ambiguous, unavailable, and time-travel scenarios.
7. Future: pilot measurement plan, generalization, and conclusion.

## Required slides

1. Cover: `AutoFlow` and “Le système prépare. L'équipe décide.”
2. Operational chaos: a morning in the agency.
3. Six frictions and their operational cost.
4. Central problem and three anti-patterns.
5. The supervised workflow: one orchestrator, three agents, one human.
6. System context and human boundary.
7. Container architecture and technology choices.
8. LangGraph workflow with routing guards and persistent human interrupt.
9. Escalation matrix: trigger, destination, and reason.
10. Three agents: understand, verify, prepare.
11. Admin workspace and the live reasoning trace.
12. Verified evaluation metrics with dataset qualifications.
13. Failure behavior and recovery paths.
14. Stack and trade-offs.
15. Generalization beyond car rental.
16. Conclusion, pilot plan, and Q&A.

## Visual direction

Create an editorial engineering deck, not a generic corporate template.

- Palette: navy `#0B1F3A`, teal `#0E9C99`, cream `#F7F4EC`, gold `#E9B44C`, red `#E74C3C`, green `#10B981`.
- Typography: Manrope for titles and a readable sans-serif for body text. Use a monospace face only for code and state names.
- Use full-bleed compositions, generous whitespace, asymmetry, strong hierarchy, and a consistent 16:9 grid.
- Use cream or very light slides for evaluation and roadmap sections to create rhythm.
- Do not use purple gradients, generic dashboard cards, stock photos, or a hero made only of text in a card.
- Use line diagrams, evidence tags, timelines, state nodes, and small interface frames.
- Use Lucide icons consistently. Do not mix random emoji styles.

## Motion and interaction

Use motion to reveal reasoning, not to decorate:

- stagger the six frictions one at a time;
- animate the workflow from intake to human review;
- reveal evidence before confidence scores;
- animate metric counters only after showing sample size and metric definition;
- highlight the exact node that receives a failure;
- show a human decision as a visible checkpoint before the workflow resumes;
- animate the time-travel experiment from +24 h to +72 h;
- provide reduced-motion support;
- never auto-advance slides;
- keep every slide usable with keyboard navigation and touch.

Required controls for HTML:
- arrow keys, PageUp/PageDown, and Space navigation;
- progress indicator;
- slide overview menu;
- fullscreen button;
- speaker-notes panel or notes in a separate file;
- print stylesheet with one slide per landscape page;
- accessible focus states and meaningful labels.

## Experiment design

Include a visible “Experiment” badge on slides 8, 12, and 13. Each experiment must state:

- input;
- expected behavior;
- observed result or current evidence;
- what the experiment does not prove.

Use these experiments: standard quote, unavailable vehicle, ambiguous dates plus discount, complaint escalation, +24 h reminder, +72 h stalled state, LLM unavailable, and unsupported evidence.

## Metrics presentation

For every number, display the definition, denominator, and qualification close to the number. Use the verified values only:

- 16 passing automated tests;
- pickup date 89%, return date 82%, vehicle category 91%, intention 100%;
- 8/8 incorrect extractions routed to a human;
- confidence >= 0.8 was fully correct in 94% of current generated examples;
- 45 simulated requests and about 370 replayed events.

Clearly separate “current technical evidence” from “pilot metrics to measure”. Never show simulated activity as business impact.

## Writing rules

- One idea per slide.
- Maximum 35 visible words on a dense slide; use speaker notes for detail.
- Prefer short verbs and concrete labels.
- Keep the French text natural and professional.
- Preserve important punchlines verbatim from the source deck.
- Explain LangGraph, `interrupt()`, evidence gates, and deterministic availability in plain language before using jargon.
- End with a precise statement of what was built, what was measured, and what the pilot must still establish.

## Final self-check

Before returning the files, verify:

- all 16 slides exist and follow the narrative;
- no unsupported business gain appears;
- no slide implies autonomous client messaging;
- all metrics have sample size or qualification;
- the human review boundary is visible in the diagrams;
- the deck can be presented without reading paragraphs;
- animation does not hide information;
- mobile and print layouts do not overlap or clip text;
- the live demo can be executed from the documented local project.

Return the files and then a concise QA report with: `FACTS USED`, `LIMITATIONS SHOWN`, `ASSETS NEEDED`, and `OPEN QUESTIONS`.
```

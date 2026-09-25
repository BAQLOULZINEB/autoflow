# AutoFlow Presentation Output Specification

This is the expected result contract for an AI assistant generating the final presentation from the context and generator prompt.

## 1. Required Files

The generated package must contain:

- `presentation.html`: self-contained interactive deck
- `presentation.md`: editable slide content or Marp/Slidev source
- `speaker-notes.md`: narration, demo cues, and timing
- `presentation-qa.md`: evidence, limitations, asset gaps, and rendering checks

## 2. Slide Contract

Each slide must include these metadata fields in the source or notes:

```yaml
slide: 1
title: "AutoFlow"
section: "Hook"
duration_seconds: 40
evidence_level: "FACT"
main_idea: "The system prepares; the team decides."
visual_asset: "none"
experiment: false
```

`evidence_level` must be one of `FACT`, `ASSUMPTION`, `SIMULATED`, `PILOT TO MEASURE`, or `LIMITATION`.

## 3. Slide-by-Slide Acceptance Criteria

| Slide | Required result | Visual test |
|---:|---|---|
| 1 | Project name and promise | Minimal cover; no crowded subtitle block |
| 2 | Operational morning and channel fragmentation | Readable five-step timeline |
| 3 | Six frictions | Six distinct visual units with short labels |
| 4 | Central problem and anti-patterns | One dominant question; anti-patterns visibly rejected |
| 5 | Supervised design choice | Large `1 / 3 / 1` structure and human checkpoint |
| 6 | System context | Client, AutoFlow, team, manager, and external services separated |
| 7 | Containers and stack | Frontend, backend, persistence, and optional LLM boundaries clear |
| 8 | LangGraph workflow | Nodes animate in execution order; guards are visible |
| 9 | Escalation matrix | Trigger maps to team or manager with reason |
| 10 | Three agents | Each agent has one verb and one safety boundary |
| 11 | Admin experience | Queue, trace, and simulation views represented without fake screenshots |
| 12 | Evaluation | Number, denominator, and qualification appear together |
| 13 | Failure behavior | Failure input flows to safe fallback or human review |
| 14 | Technical trade-offs | Choice, reason, and rejected alternative shown |
| 15 | Generalization | Car rental is the first instance of a reusable workflow skeleton |
| 16 | Conclusion and pilot plan | Built, measured, unknown, and next step are distinct |

## 4. Interactive Experiment Contract

The HTML deck must include an experiment mode or an experiment panel. Each experiment needs a `Run` or `Replay` control and must show the following states:

### Experiment A: Standard quote

- Input: complete request with dates and vehicle category.
- Expected: structured request, availability result, quote draft, human review.
- Evidence: workflow path and final state.
- Does not prove: business conversion or revenue impact.

### Experiment B: Unavailable vehicle

- Input: request that overlaps an existing booking.
- Expected: no invented availability; alternatives with readable reasons.
- Evidence: deterministic availability node and exclusion reasons.
- Does not prove: real-world fleet accuracy beyond the demo dataset.

### Experiment C: Ambiguity and discount

- Input: ambiguous dates plus a discount request.
- Expected: clarification, then manager escalation after completion.
- Evidence: two human checkpoints and state transitions.
- Does not prove: manager policy is valid for every agency.

### Experiment D: Failure and recovery

- Input: unavailable LLM or unsupported extracted field.
- Expected: rules-only fallback or evidence-gated rejection, followed by human review.
- Evidence: `llm_failed`, confidence adjustment, missing field, or rejected field.
- Does not prove: resilience against every external provider outage.

### Experiment E: Time travel

- Input: accepted quote with no customer reply.
- Expected: reminder at +24 h and `stalled` plus human action at +72 h.
- Evidence: clock change, follow-up event, and state transition.
- Does not prove: customer behavior or actual response improvement.

## 5. Metrics Contract

Every metric component must render:

```text
metric name
value
numerator / denominator
dataset or source
evidence level
limitation
```

Required current technical metrics:

- `16 / 16` automated tests passing.
- `39 / 44 = 89%` pickup-date accuracy.
- `36 / 44 = 82%` return-date accuracy.
- `40 / 44 = 91%` vehicle-category accuracy.
- `45 / 45 = 100%` intention accuracy.
- `8 / 8 = 100%` incorrect extractions routed to a human.
- `94%` fully correct among current examples with confidence at least `0.8`.

Required future pilot metrics must be rendered as empty baseline/after fields or “to measure”, never as completed values:

- time to first response;
- time to quote readiness;
- first-message completeness;
- follow-up completion;
- manual minutes per request;
- escalated-case percentage.

## 6. Speaker Notes Contract

For each slide, include:

- one sentence stating the point;
- a 20-60 second spoken script;
- one transition sentence;
- one likely jury question;
- one evidence or limitation reminder.

For slides 12 and 13, the notes must explicitly explain the evaluation-set limitation and the difference between technical correctness and business impact.

## 7. Rendering and UX Checks

The final HTML passes when:

- it opens directly in a browser without a build step;
- keyboard navigation works with `Left`, `Right`, `PageUp`, `PageDown`, and `Space`;
- overview and fullscreen controls work;
- the progress bar reflects the current slide;
- animations can be disabled with `prefers-reduced-motion`;
- no text, diagram, table, or control overlaps at 1366x768 and 390x844;
- print preview creates one slide per landscape page;
- every image has alt text or is a labeled placeholder;
- no external API call is required for the presentation to run;
- the final slide can be reached even if JavaScript animation fails.

## 8. Final QA Report Template

```markdown
# Presentation QA

## FACTS USED
- [list the verified project facts and metrics]

## LIMITATIONS SHOWN
- [list dataset, pilot, integration, and business-impact limitations]

## EXPERIMENTS INCLUDED
- [list each experiment and expected result]

## ASSETS NEEDED
- [screenshots, diagrams, logos, or placeholders still required]

## OPEN QUESTIONS
- [questions that require the author or agency to answer]

## RENDER CHECKS
- [ ] desktop layout
- [ ] mobile layout
- [ ] keyboard navigation
- [ ] reduced motion
- [ ] print/PDF layout
- [ ] no unsupported metrics
```

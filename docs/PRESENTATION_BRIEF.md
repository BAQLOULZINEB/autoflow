# AutoFlow — brief de génération d’une soutenance gagnante

## Storyline

Tell one coherent story: a client request arrives incomplete; AutoFlow prepares reliable work; a human keeps ownership of every commercial decision; the system leaves an auditable trace. Avoid selling an autonomous chatbot.

## Slide plan (11 slides, 9–11 minutes)

1. **Title — AutoFlow: supervised workflow automation for a car-rental agency.** One sentence: *the system prepares; the team decides.*
2. **The operational friction.** Use `rapport_assets/figures/fig_infographie_probleme_solution.png`. Explain fragmented requests, manual availability checks and forgotten follow-ups as hypotheses to validate on site.
3. **Design principle.** “No invented availability. No client message without a human click. Every decision is traceable.”
4. **Human-centred workflow.** Use `fig_graphe_langgraph.png`. Explain the orchestrator and three narrow agents.
5. **State and responsibility.** Use `fig_machine_etats.png`. Emphasize illegal-transition blocking and escalation states.
6. **One rich business scenario.** Use `fig_sequence_scenario_c.png`. Walk through ambiguous dates + discount → two human interruptions.
7. **Operator experience.** Use `fig_admin_queue.png` and `fig_admin_live_trace.png`. Explain what the staff member sees and decides.
8. **Engineering choices.** React/Vite, FastAPI, SQLAlchemy, LangGraph, rules-first extraction, optional LLM with evidence gate.
9. **Validation, not hype.** Show `16 passed`; the controlled evaluation numbers; visually isolate “fictional labelled sample” and “not a business KPI.”
10. **Limits and responsible deployment.** Real-message evaluation, agency audit, privacy, no automatic sending, pilot measurement before any ROI claim.
11. **Pilot proposal.** “30 minutes to map one real request; 2–4 weeks to measure before/after; continue only if the agency validates the gain.”

## Visual direction

Use navy `#0B2434`, teal `#62D2C8`, warm amber `#F6B65B`, and cream `#FFFDF7`. Use one message per slide, large type and the locally packaged diagrams. Keep every slide readable from three metres away.

## Questions to pre-answer

- **Why use AI instead of a simple form?** AI assists interpretation of varied natural-language messages; deterministic logic remains responsible for availability and business rules.
- **Why three agents?** Each has one testable responsibility: understand, verify, prepare. More agents would add coordination risk without business value.
- **Can the system send offers itself?** No. It only prepares drafts; a person approves, edits or rejects them.
- **Are the metrics real?** The engineering and controlled-evaluation metrics are real and reproducible; business metrics must be measured in the pilot.

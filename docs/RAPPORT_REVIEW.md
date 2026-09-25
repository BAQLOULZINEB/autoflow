# Revue académique — AutoFlow V1.1

## Verdict

The project has a credible engineering core: the business problem is clear, the workflow is explicit, the human decision gate is structural rather than decorative, and the repository provides runnable tests and an evaluation script. The report is strongest when it explains this discipline of supervised automation.

The V1 report needed four corrections before being suitable for an academic jury:

1. The report mixed synthetic demonstration data, evaluation data and later Excel-import data. V1.1 makes their roles explicit.
2. It stated performance too broadly. V1.1 reports the exact scope: 45 fictional labelled messages and eight observed extraction errors.
3. A confidence statement did not match the generated evaluation report. It now reports `36/36` fully correct extractions at confidence ≥ 0.8 within the controlled sample and explains why this is not a generalisation claim.
4. The test suites still used the old administrator token after the application token changed. They now inject their own test-only token, so the result is reproducible without weakening the configured application token.

## Evidence verified on 25 September 2026

| Check | Result | Meaning |
|---|---:|---|
| `pytest -q` | 16 passed | Eight workflow tests and eight simulation/catalogue tests pass. |
| `python -m eval.eval_intake` | 45 labelled fictional messages | Field accuracy: pickup 39/44, return 36/44, category 40/44, intent 45/45. |
| Human routing of observed extraction errors | 8/8 | A routing result inside the controlled sample, not a field guarantee. |
| Figures required by `IMAGES.md` | 10 report figures packaged | Logos have a compile-safe textual fallback until official files are supplied. |

## Remaining academic requirements

- Replace the four cover placeholders and, if required by EMSI, add authorized official logo files.
- Ask the supervising teacher to validate the exact internship title, host organisation and academic-year wording.
- Run a short on-site audit before writing any claim about response time, conversion, staff workload or financial impact.
- Collect a separately consented and anonymised real-message corpus before reporting LLM performance. The current evaluation is rules-only and synthetic.
- Keep the reference PDF as a design input; it must not be presented as field-study evidence.

## Recommended oral defense positioning

Do not frame AutoFlow as “an autonomous car-rental AI.” Frame it as an AI-engineering system that turns dispersed customer requests into a supervised, traceable decision workflow. Demonstrate one sensitive scenario: ambiguous dates, deterministic availability check, manager interruption, then traceable approval. This is the strongest evidence of technical judgment in the project.

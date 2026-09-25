# Package Overleaf — AutoFlow

This folder makes both reports self-contained. Upload either `rapport.tex` (full version) or `rapport_visuel.tex` (concise visual version), together with the complete `rapport_assets/` folder, to the root of an Overleaf project. Set the selected file as the main file and compile with pdfLaTeX.

## Contents

| Path | Purpose | Origin |
|---|---|---|
| `figures/fig_infographie_probleme_solution.png` | Problem → supervised workflow → outcome visual | Existing project asset listed in `docs/IMAGES.md` |
| `figures/fig_c4_*.png` | Context, containers and deployment architecture | Locally exported from `docs/diagrams/*.html` |
| `figures/fig_graphe_langgraph.png` | Executable orchestration workflow | Locally exported from `docs/diagrams/03-workflow.html` |
| `figures/fig_machine_etats.png` | State machine and legal transition overview | Exported from `sources/fig_machine_etats.svg` |
| `figures/fig_sequence_scenario_c.png` | Sequence of the ambiguous-discount scenario | Exported from `sources/fig_sequence_scenario_c.svg` |
| `figures/fig_admin_*.png` | Interface navigation, traceability and simulation schematics | Exported from the corresponding editable SVG sources |
| `figures/logoEmsi.png`, `figures/honoris_logo.png` | Institutional marks displayed on the cover | Extracted from the project owner's supplied previous report PDF |
| `sources/*.svg` | Editable figure source files | Created from the architecture and evaluation specifications in `docs/IMAGES.md` and `docs/02-architecture.md` |
| `references/proposition_visuelle_3_pages_fr.pdf` | Visual proposal supplied by the project owner | Reference only; not embedded in the academic report |
| `references/workflow_supervision_reference.png` | Workflow visual supplied by the project owner | Reference only; not embedded in the academic report |

## Logos and cover

The package includes the two institutional marks recovered from the supplied previous report. Both files can be replaced only with authorized official assets named exactly:

- `rapport_assets/figures/logoEmsi.png`
- `rapport_assets/figures/honoris_logo.png`

Before submission, update the four commands near the top of `rapport.tex`: `\reportauthor`, `\academicadvisor`, `\companyadvisor`, and `\hostcompany`.

## Reproducibility

The report distinguishes generated V1 data used for evaluation from a later Excel import module. The claimed controlled results can be rerun from `backend/` with:

```powershell
..\.venv\Scripts\python.exe -m pytest -q
$env:PYTHONIOENCODING = 'utf-8'
..\.venv\Scripts\python.exe -m eval.eval_intake
```

The expected validation result at the time of preparation is `16 passed`. The numerical evaluation is based on 45 fictional labelled messages; it is not a claim of performance at an agency.

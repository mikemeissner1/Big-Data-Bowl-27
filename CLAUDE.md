# CLAUDE.md

Project: NFL Big Data Bowl 2027, "Combine to NFL Performance". Link 10 Hz Combine sensor
tracking to NFL regular-season performance for one position, drill or movement.
Open track, solo (Mike). **Deadline: Jan 6, 2027, 11:59 PM UTC.**
Submission: Kaggle Writeup (<= 2,000 words, < 10 figures/tables) + public Kaggle Notebook
using the tracking data. Judging: Football 30, Data Science 30, Writeup 20, Visualization 20.

## Working rules

1. **Read `docs/` before any task** (start with `docs/playbook.md`, then `docs/decisions/`
   and the tail of `docs/log.md`).
2. **Before running code, explain in plain terms what it does and why.** Mike is refreshing
   his data science skills and wants to stay in the loop.
3. **Stop and ask when a method choice (target, features, model, validation) is not already
   recorded in `docs/decisions/`.** Offer options, trade-offs and a recommendation; write the
   decision as a note from `docs/decisions/TEMPLATE.md` once Mike decides.
4. **Never commit anything in `data/`.** Raw files in `data/raw` are read-only inputs.
5. Pin dependencies (`uv.lock`) and **set random seeds** everywhere randomness is used.
6. **Every figure is generated from code** and saved to `reports/figures/`. No hand-made charts.
7. **Always include a naive baseline** before any model, then a simple baseline, then the
   fancier model.
8. **Grouped cross-validation** (e.g. by player) with an **untouched holdout** kept until the end.
9. **Report uncertainty and calibration** (confidence intervals, calibration plots), not just
   point estimates.
10. **Flag weak or null results honestly.** A clear negative result beats a dressed-up one.
11. **Explain methods plainly, and say how Mike would explain each to an NFL GM.**
12. Logic lives in `src/bdb27/`; notebooks (`notebooks/`, paired .py via jupytext) are for
    exploration. Polars for tracking data, pandas for small tables.
13. **Work on branches and open PRs for Mike**; do not merge.
14. **End of each session:** append to `docs/log.md` (done, found, open) and add any new
    method to `docs/learning.md`.
15. Hold analysis, writing, figures and documentation to a high industry standard. Cite
    sources for research claims; never invent papers, results or numbers.

## Commands

```bash
make setup   # uv sync + create data folders
make lint    # ruff check + format check
make test    # pytest
make lab     # JupyterLab
```

Machine: Apple M3 Pro, 18 GB RAM. Prefer Parquet, lazy polars (`scan_*`) and chunking over
loading whole tracking files.

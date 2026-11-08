# Playbook

**Phase 1 is a collaborative brainstorm with Mike in the Claude project.** Research, topic
selection and method choices are discussed there in depth, then recorded here and in
`docs/decisions/`. This playbook is a guide, not a script: reorder or skip steps when the data
or Mike says so. Mike makes the decisions.

## Milestones (back from Jan 6, 2027)

| Date | Milestone |
|---|---|
| Nov 22 | Research done and topic chosen |
| Dec 6 | Working baseline (naive baseline + simple model, end to end) |
| Dec 20 | Final model and figures |
| Jan 3 | Writeup and Kaggle Notebook polished (3 days of buffer) |
| Jan 6, 11:59 PM UTC | Deadline |

About 5 hours/week: keep tasks small, finish one visible thing each week.

## 1. Data audit
What is actually in the 9 files: players, positions, drills, sampling, missingness, tracking
quality, how Combine rows join to NFL performance. Counts per position (about 100 players per
group) set what is statistically feasible. Output: `docs/research/data-audit.md`.

## 2. Literature
Relevant papers on athletic testing and NFL performance, tracking-data methods, and statistical
methods for small samples. Cite every claim with its source; do not invent references.
Output: `docs/research/literature.md`.

## 3. Past winners
What earlier Big Data Bowl winners and finalists did, why they won, how they scored on football,
data science, writeup and visualization. Output: `docs/research/past-winners.md`.

## 4. Kaggle submission rules
Writeup and Notebook limits, public notebook requirements, how tracking data is accessed in a
Kaggle notebook, and **whether interactive content (Plotly, widgets, embeds) is allowed in
Writeups and how it renders in Notebooks**. Output: `docs/research/kaggle-rules.md`.

## 5. Candidate topics
Score each candidate 1-5 on: feasibility, football value, novelty, method strength,
explainability, visual potential, and risk (5 = low risk). Weight by the judging split:

| Judging criterion (weight) | Dimensions feeding it |
|---|---|
| Football (30) | football value, novelty |
| Data Science (30) | method strength, feasibility, risk |
| Writeup (20) | explainability |
| Visualization (20) | visual potential |

Keep the scoring table in `docs/research/topics.md`. Scores inform the decision; they do not make it.

## 6. Method checklist
- Define the **target** and the **prediction-time information set** first (what is known when
  the prediction would be made).
- Naive baseline, then simple baseline, then fancier models.
- Grouped CV (by player) plus an untouched holdout used once at the end.
- Confidence intervals and calibration.
- Careful importance (permutation importance or SHAP), with caveats for correlated features.
- Figures generated from code only.
- Pinned environment and fixed seeds.

## 7. Decision log
Each decision is a note in `docs/decisions/` (copy `TEMPLATE.md`). Index:

| # | Decision | Status |
|---|---|---|
| 0001 | Environment and repo tooling: uv, `src/` layout, polars + pandas, notebooks via jupytext | decided 2026-11-08 |

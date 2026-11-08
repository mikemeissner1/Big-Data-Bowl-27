# NFL Big Data Bowl 2027: Combine to NFL Performance

Solo entry, **Open track**. Deadline: **Jan 6, 2027, 11:59 PM UTC**.

The 2027 competition asks entrants to link 10 Hz NFL Combine sensor tracking to
NFL regular-season performance, focused on one position, drill or movement. The submission is a
Kaggle Writeup (<= 2,000 words, < 10 figures/tables) plus a public Kaggle Notebook that uses the
tracking data. Judging: Football 30, Data Science 30, Writeup 20, Visualization 20.

**Status:** research and topic selection (see [`docs/playbook.md`](docs/playbook.md)). No topic chosen yet.

## Set up

Requires [uv](https://docs.astral.sh/uv/) (`brew install uv` on macOS).

```bash
git clone https://github.com/mikemeissner1/Big-Data-Bowl-27.git
cd Big-Data-Bowl-27
make setup          # uv sync: builds .venv with the pinned dependencies
make test           # confirm everything works
```

Put the competition CSVs in `data/raw/` (not committed; see [`docs/data.md`](docs/data.md)), then:

```bash
uv run python -m bdb27.data      # converts data/raw/*.csv to Parquet in data/interim/
make lab                         # JupyterLab for exploration
```

## Layout

| Path | Purpose |
|---|---|
| `src/bdb27/` | Reusable code (data loading, features, models, plots) |
| `notebooks/` | Exploration; paired `.py` files via jupytext (see its README) |
| `tests/` | pytest tests |
| `docs/` | Playbook, decision notes, research, session log, learning notes |
| `reports/figures/` | Figures generated from code |
| `data/{raw,interim,processed}/` | Local only, gitignored |

## Reproduce

`uv sync` recreates the exact environment from `uv.lock`; all figures and results come from code in `src/` and `notebooks/`. Random seeds are fixed and each modeling choice is recorded in `docs/decisions/`.

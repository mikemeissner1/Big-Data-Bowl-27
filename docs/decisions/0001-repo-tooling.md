# Decision 0001: Environment and repo tooling

- **Date:** 2026-11-08
- **Status:** decided

## Question
How do we manage Python environments, project layout and dataframes?

## Options and choice
- **Environment:** uv (fast, one lockfile) over pip/conda.
- **Layout:** `src/bdb27/` package, notebooks for exploration only.
- **Dataframes:** polars for the large tracking files (lazy, low memory), pandas for small tables.
- **Notebooks:** paired `.py` (jupytext percent) so Claude and git can work with plain text.
- **Who writes the scaffold:** a Claude project thread, not terminal Claude Code.

## Trade-offs
Polars has a smaller ecosystem than pandas, but the tracking files are too big for comfortable
pandas on 18 GB RAM; converting at the boundary is easy.

## Mike's decision
Approved all of the above (2026-11-08).

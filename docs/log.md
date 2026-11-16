# Session log

Newest entries at the bottom. At the end of each working session, append an entry.

## Template

```
### YYYY-MM-DD: short title
- **Done:** what was completed
- **Found:** what we learned (including null or surprising results)
- **Open:** unresolved questions and next step
```

## Entries

### 2026-11-08: Repo scaffold
- **Done:** project layout, uv environment, ruff/pytest config, docs skeleton, data-loading stub.
- **Found:** n/a
- **Open:** run `make setup` locally; then data audit (playbook step 1).

### 2026-11-14: CSV to Parquet conversion (8 of 9 files)
- **Done:** ran `bdb27.data.csv_to_parquet` on all 9 raw CSVs (raw untouched). 8 converted to `data/interim/`, row counts match raw line counts minus header; each took about 1 s or less (the 1 GB `game_tracking_2025` took 1.0 s, peak memory about 1.3 GB). Parquet is about 5-6x smaller for the big files. I deleted the truncated `player_play.parquet` the failed run left behind.
- **Found:** **`player_play.csv` failed**: `NA` appears in `pre_snap_home_team_win_probability` (loader inferred Float64 from the first 10k rows; `NA` is a missing-value marker). Also, `NA` is read as the literal string in all columns of `combine_results` (forty, vertical, broad_jump, three_cone, short_shuttle, ten_yd_split, bench_reps, two ngs scores) and `players` (draft_round, draft_pick_within_round, draft_overall_pick), so they are String, not numeric. Timestamps (`time`) and `birth_date` are String, not Datetime. Not fixed, on instruction.
- **Open:** decide how to treat `NA` (add `null_values=["NA"]` in the loader) and whether to parse dates; then re-run `player_play`. Needs a note in `docs/decisions/`. Then the data audit.

### 2026-11-14: Fix `NA` handling and re-run conversion (9 of 9)
- **Done:** Mike approved `null_values=["NA"]` (docs/decisions/0002). Added it to `csv_to_parquet` in `src/bdb27/data.py`; re-ran `convert_all(overwrite=True)`: all 9 CSVs converted in 2.6 s, `player_play.parquet` now exists (314,197 rows, 64 cols). Row counts of the other 8 are unchanged. pytest, ruff check and ruff format pass. Raw files untouched.
- **Found:** the cause of the failure was `NA` text in `pre_snap_home_team_win_probability` (first `NA` at row 24,107, past the 10,000-row type guess). `NA` columns in `combine_results` and `players` are now numeric. `game_tracking.event` is now null for about 93% of frames.
- **Open:** `player_play.rush_yards` is still String with the 10,000-row guess (full-file guess gives Int64); `time` and `birth_date` are still String. Both need a decision note. Then the data audit.

- **Update (same day):** Mike also approved the full-file type guess. `csv_to_parquet` now uses `infer_schema_length=None`; re-ran all 9 (37.4 s total, versus 2.6 s before). `player_play.rush_yards` is now Int64. 
- **Update 2 (same day):** Mike approved date parsing. Added `try_parse_dates=True`; only `time` (4 tracking files) becomes Datetime and `players.birth_date` becomes Date; `game_clock` stays text. Checked: parsed `time` round-trips exactly to the raw text (milliseconds kept), no null times, frames 100 ms apart, `birth_date` has no nulls. Re-ran all 9 (133.7 s total; parsing makes the run slower, and it only needs to run once). Row counts unchanged.
- **Open:** data audit (playbook step 1). Branch and PR for these changes are with the facilitator.

### 2026-11-15: Data audit (playbook step 1)
- **Done:** profiled all 9 Parquet files with polars; wrote `docs/research/data-audit.md` (6 questions, surprises, open questions, one-page summary). New code: `src/bdb27/audit.py` (all tables, `python -m bdb27.audit`) and `src/bdb27/audit_figures.py` (2 figures in `reports/figures/`). Work is on branch `research/data-audit`, not committed. No topic proposed.
- **Found:** only 510 Combine players (classes 2023-25) exist, and game tracking contains **only those players** (no opponents, teammates or ball). IDs link perfectly (0 orphans; 13 players never played, confirmed by the NFL career file). Only the 40-yard dash has broad coverage (418 sensor traces, 82%); 3-cone/shuttle/bench missing for 60-65%. 109 players (21%) have no regular-season snap; median rookie has 102. WR/TE rows are pass plays only; DBs in coverage have no outcome column. Combine `dis` disagrees with `s` and positions (game-file `dis` is fine). Sensor 40 times correlate 0.91 with official but run 0.36 s slower. 8% of career snaps not in the data.
- **Open:** how the 510 were selected; definitions of Combine `dis`, `blitzing` and the 40 sensor clock; whether OL/DB drill traces include a sprint phase; how many very short 3-cone/shuttle traces exist. Next: playbook step 2 (literature) or whatever Mike redirects to. Branch, commit and PR are with Mike.

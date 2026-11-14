# Decision 0002: Treat `NA` as missing when converting CSV to Parquet

- **Date:** 2026-11-14
- **Status:** decided

## Question
The raw CSVs use the text `NA` for missing values. How should the CSV-to-Parquet loader treat it?

## Options
1. **Leave as is:** `NA` is read as ordinary text. This broke `player_play.csv` (polars guessed a
   number type for `pre_snap_home_team_win_probability`, then hit `NA` at row 24,107) and left
   numeric columns in `combine_results` and `players` stored as String.
2. **`null_values=["NA"]`:** polars reads `NA` as a true missing value, so numeric columns become numeric.

## Trade-offs
| | Option 1 | Option 2 |
|---|---|---|
| Strength | No change | Fixes the failure; columns get proper numeric types |
| Weakness | Fails; types wrong | `NA` can no longer be told apart from other missing values (no other missing marker was found) |
| Easy to explain to a GM? | n/a | Yes: "NA means not recorded, so we store it as missing" |

## Recommendation
Option 2.

## Mike's decision
Approved `null_values=["NA"]` (2026-11-14). Also approved the full-file type guess (`infer_schema_length=None`) the same day, and date parsing (`try_parse_dates=True`) too.

## Type guessing
With `infer_schema_length=10_000`, `player_play.rush_yards` was read as String (all `NA` in the
first 10,000 rows). The loader now uses a full-file guess (`None`), which reads it as Int64. Cost: one
extra pass per file.

## Date parsing
`try_parse_dates=True` turns `time` (combine and game tracking, e.g. `2024-01-07T21:46:07.700`) into
Datetime and `players.birth_date` (e.g. `2001-09-02`) into Date. Tested on all 9 files: no other
column is affected (`game_clock` stays text).

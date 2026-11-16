# Data audit

**Date:** 2026-11-15 · **Branch:** `research/data-audit` · **Scope:** playbook step 1. This audit
describes the data. It does **not** propose a topic.

**Reproduce:** `uv run python -m bdb27.audit` prints every table below; `uv run python -m
bdb27.audit_figures` redraws the two figures. Everything reads the Parquet files in
`data/interim/` (polars; the three big game-tracking files are scanned lazily). Raw CSVs were not
touched. Counts are exact; "about" is used only for rounded shares.

**Conventions.** *Position group* = `combine_results.combine_position` (DB, DL, OL, WR, TE).
*Snap* = one `player_play` row (a scrimmage play the player was on the field for). *Regular
season* = `games.season_type == 'REG'`. *Rookie season* = the season equal to the player's draft
year.

---

## 0. The one thing to know first

**This is not "all NFL players". It is a fixed list of 510 Combine participants (draft classes
2023, 2024, 2025), and the in-game tracking contains only those 510 players: no opponents, no
teammates, no ball.** Every in-game file is keyed to those same 510 `nfl_id`s. That shapes every
question below.

---

## 1. Players

510 players, 3 draft years (2023: 160, 2024: 177, 2025: 173). 383 were drafted (rounds 1-7) and
127 (25%) were undrafted (draft fields null). Every one of the 510 has Combine scalar results,
career totals and Combine sensor traces.

| Position group | 2023 | 2024 | 2025 | Total |
|---|---|---|---|---|
| DB | 35 | 50 | 37 | **122** |
| OL | 37 | 46 | 38 | **121** |
| DL | 37 | 37 | 44 | **118** |
| WR | 39 | 31 | 37 | **107** |
| TE | 12 | 13 | 17 | **42** |

**Surprises**
- **No QB, essentially no RB (1), no LB group.** The Combine's own grouping has no "LB": the
  30 players listed as `OLB` in the NFL (plus ILB/MLB) sit under "DL" or "DB".
- **`nfl_position` is finer, but several labels are tiny:** WR 106, CB 60, G 51, T 50, DT 47,
  TE 42, DE 36, OLB 30, SS 28, FS 25, C 20, then DB 5, NT 5, ILB 2, RB 1, FB 1, MLB 1.
  Five players labelled just "DB" never took a regular-season snap.
- **Hybrids exist.** Combine "DBs" lined up at OLB for 6,286 snaps and at MLB for 1,699;
  Combine "DL" lined up at slot CB for 618.
- **Selection is unexplained.** 510 players over three years is about 170 a year; the draft alone
  has about 257 picks a year. We do not know how these players were chosen (maybe those with
  sensor data who later had tracking). Anything we find is about *this* sample.

### Which drills are recorded

**Two kinds of Combine data:**
1. **Scalar results** (`combine_results`): `forty`, `ten_yd_split`, `vertical`, `broad_jump`,
   `three_cone`, `short_shuttle`, `bench_reps`, plus height, weight, hand size, arm length, wing
   span, and three NFL-computed scores (`ngs_*`).
2. **10 Hz sensor traces** (`combine_tracking`), only for these drills:
   - **Standard drills:** 40-yard dash, 3-cone, short shuttle.
   - **Position drills:** `SKILL_DRILLS_DB / DL / OL / WR / TE / LB` (about 8-14 drills each).
   - **No sensor traces exist for vertical jump, broad jump or bench press**: scalar only.

**Completeness for the standard drills (players with data, out of the group size):**

| Group (n) | 40 scalar | 40 sensor | 3-cone scalar | 3-cone sensor | Shuttle scalar | Shuttle sensor |
|---|---|---|---|---|---|---|
| DB (122) | 104 | 102 | 25 | 24 | 33 | 28 |
| DL (118) | 94 | 93 | 43 | 45 | 46 | 38 |
| OL (121) | 95 | 95 | 61 | 48 | 64 | 54 |
| WR (107) | 97 | 94 | 33 | 24 | 38 | 29 |
| TE (42) | 34 | 34 | 18 | 19 | 20 | 21 |
| **All (510)** | **424** | **418** | **180** | **160** | **201** | **170** |

- **Only the 40-yard dash has broad coverage** (about 82% of players). The 3-cone and shuttle are
  about 35-40%, because most athletes skip them. Vertical (438), broad jump (423) and 10-yard
  split (425) are about 83-86% (scalar only); bench press is 192 (38%).
- For the 40, every sensor player also has a scalar time, plus 6 scalar-only players. The 3-cone
  and shuttle disagree in both directions (10 sensor-only, 30-41 scalar-only).
- **Position drills are well covered inside each group** (most core drills have 98-122 of ~107-122
  players for DB/OL/WR/DL, about 40 of 42 for TE), but the **LB drill group has only 4 players**.
- **Drill names are messy.** The same drill appears under variant spellings:
  `PASS_PRO-MIRROR_DRILL` (84) vs `PASS_PRO_MIRROR_DRILL` (37); `SPEED_OUT_LEFT` (31) vs
  `SPEED_OUT_ROUTE_LEFT` (76); `OVER_SHOULDER_ADJUST` vs `OVER_THE_SHOULDER_ADJUST` (TE);
  `LINE` (33) vs `LINE_DRILL` (85) for DB; four `SHORT_ZONE_BREAK*` variants for DL. They must be
  merged before counting "players with a drill".

### What to know about the Combine scalar results

(Exploratory checks, 2026-11-15; Spearman rank correlations, pairwise-complete players.)

- **Body size drives everything.** Pooled across positions the 40 correlates 0.87 with weight, 0.69
  with height; broad jump -0.77 with weight. The drills are also highly inter-correlated (40 vs
  10-yd split 0.91, 3-cone vs shuttle 0.91, 40 vs broad jump -0.84). So raw pooled results mostly say
  "big vs small", and the drills carry overlapping information. Anything we do must standardize
  **within position group** and expect strong collinearity.
- **No drift by draft year in the scalars.** Mean 40: 4.736 (2023), 4.736 (2024), 4.727 (2025);
  WR mean 40 4.50 / 4.45 / 4.46 (n about 30-35 each). The sensor-vs-official 40 offset does drift,
  so the scalars are the steadier record.
- **`ngs_athleticism_score` is a position-adjusted composite of the drills.** Pooled it barely
  correlates with the 40 (-0.23), but within group it does (DB -0.69, DL -0.43, OL -0.78, WR -0.71,
  TE -0.63). Treat it, and `ngs_final_score`, as derived from the same Combine numbers (and
  `ngs_college_production_score` from college stats): using them alongside the drills double-counts,
  and the final score blends in information that is not Combine.
- **Draft capital dominates playing time.** Rookie-season regular-season snaps vs draft pick
  (undrafted = after the last pick): Spearman **-0.74** overall (DB -0.70, DL -0.69, OL -0.83,
  WR -0.74, TE -0.82). Against 40 time the relationship is weak (-0.06 to -0.25). Median rookie
  snaps by round: R1 774, R2 490, R3 284, R4 228, R5 90, R6 72, R7 11, undrafted 0; 92% of
  first-rounders reach 250 snaps vs 4% of undrafted players. Opportunity is mostly decided by
  where a team drafted the player, so any "athletic test predicts performance" result is confounded
  by draft position unless it is controlled for.
- **Skipping drills is related to draft status, but weakly and not uniformly.** 21% of undrafted
  players vs 15% of drafted players have no 40; by group the direction even flips for DL.
  Missingness remains non-random but is not simply "bad players skip".

---

## 2. Combine sensor tracking

**Size and structure.** 463,189 rows. One `event_id` = one player's one attempt at one drill:
6,310 events. `PLAYER` rows 431,094; `BALL` rows 32,095 (the ball appears only in WR and TE
route-drill traces, and not in every one: one example WR's slant route has no ball rows; coverage
not yet measured). Columns: position `x, y`, speed `s`, acceleration `a`, `dis`, direction `dir`
(no orientation `o`).

| Drill | Traces | Frames per trace (min / median / max) | Median top speed (yd/s) |
|---|---|---|---|
| 40-yard dash | 793 | 45 / 51 / 90 | 10.6 |
| 3-cone | 203 | 10 / 79 / 101 | 6.6 |
| Short shuttle | 223 | 11 / 51 / 202 | 5.8 |
| Position drills (DB, DL, LB, OL, TE, WR) | 5,091 | minimum 21-44, median 50-91, maximum up to 209 | 6.8-8.4 |

**Sampling rate: exactly 10 Hz, no gaps.** All 456,328 consecutive-frame pairs inside a trace are
exactly 100 ms apart. A 40-yard trace is about 5 seconds (about 51 frames); players have 1 or 2
traces per 40 (43 players have 1, 375 have 2).

**Sensor errors: none obvious.** No nulls, no duplicate rows, no duplicate (event, player, time).
Top speed 11.85 yd/s (about 24 mph) and top acceleration 10.7 yd/s² are physically possible;
no frame above 12 yd/s. Only 5 frames have |a| above 10.

**Things that are not errors but matter:**
- **`dis` breaks its own definition.** The data dictionary says `dis` is "distance traveled from
  the previous tracking frame in yards", but in the Combine file it does not match the change in
  `x, y`: summed over a trace it is only **61%** of the true path length (40-yard dash 90%, short
  shuttle 38%, 3-cone 34%, OL drills 40%), and only 1.5% of frames agree within 0.01 yd. It is not
  a simple lag of `s` either (tested lags 0-3 frames). Meanwhile `s` matches the change in `x, y`
  to within about 0.05 yd/s, and in the *game* files `dis` is fine (median gap 0.003 yd). **Use
  `s` and `x, y`, not `dis`, for Combine traces**, and compute distance from positions. The
  pattern (worst in change-of-direction drills) hints at a smoothed or longer-window quantity, but
  the cause is unknown.
- **All drills sit in one fixed field frame.** The same drill starts and ends within about a yard
  for every player and every year (for example the slant route starts at x 24.1-24.8, y
  43.3-44.3), so paths are directly comparable.
- **40-yard traces start slightly past the line** (x about 10.3-11) and run to about x 51. Starting
  from the first frame, 160 of 793 traces (20%) never quite cover 40 yards (maximum 38.5-40.0).
  That is a window artifact, not athletes stopping.
- **Attempt labels are labels, not counts.** `attempt` runs up to 17 for some drills, though a
  player has at most 2 traces of the 40.
- **2023 event IDs use a different format** (`6414e684…-2023`) from 2024 and 2025
  (`20250302…_000`), so the 2023 data came through a different pipeline. Harmless as a key, but
  a hint to check 2023 for other differences.
- **A few traces are very short** (min 10-11 frames for the 3-cone and shuttle: about one second).
  They cannot be complete reps. I have not counted how many; do that before using those drills.

**Do the sensor traces agree with the official 40 time?** Crude check: time to cover 40 yards from
the first frame, versus the published `forty`. Across 633 traces the sensor time is **0.36 s
slower** on average (SD 0.15 s), drifting by year (+0.30, +0.36, +0.41 s for 2023/24/25). For each
player's best attempt, sensor and official time **correlate at 0.91** (n = 381 players). So the
two agree on who is fast, but they do not agree on the clock: the official clock probably starts at
first movement and the trace starts earlier. This is a definition issue to resolve, not proof the
sensor is wrong.

**Figures** (generated by `bdb27.audit_figures`; players chosen by a fixed rule: closest to the
position group's median 40 time among players with the drill):
- `reports/figures/audit_combine_40_speed.png`: speed over time in the 40 for a typical WR (4.46 s,
  `nfl_id` 55904), DB (4.49 s, 57185) and OL (5.15 s, 57189). The curves are smooth and the OL
  is visibly slower and flatter.
- `reports/figures/audit_combine_drill_paths.png`: the same three players' paths in a position
  drill (WR slant route, OL 5-yard wave, DB W-drill).
  **Caution:** the OL and DB traces contain a slow shuffle phase (about 2 yd/s for 5-12 s) followed
  by a fast straight run (6-7 yd/s, 15 yards). I cannot tell from the data whether the sprint is a
  designed part of the drill or extra recording; position-drill traces will need phase
  segmentation before use.

---

## 3. In-game tracking, snaps and context

**What exists.** Three season files plus `player_play` (per-play context and outcomes) and `games`.

| File | Rows | Games | Plays | Distinct players |
|---|---|---|---|---|
| `game_tracking_2023` | 3,665,443 | 333 | 31,690 | 156 |
| `game_tracking_2024` | 7,827,944 | 334 | 40,331 | 318 |
| `game_tracking_2025` | 11,160,903 | 334 | 42,544 | 448 |
| `player_play` (all) | 314,197 rows | 1,001 | 114,954 | 497 |

- The panel grows because each draft class joins in its rookie year (no player appears before
  their draft year). Every game of every season (preseason, regular season, playoffs) is present
  except 1 of 1,002 games.
- **Only the 510 players are tracked, 1 to 11 per play** (usually 1-4), and the median player-play
  is 69 frames (about 6.9 s). There are **no opponents, teammates or ball**, so anything that
  needs a second player (separation, pressure geometry, coverage matchups) cannot be recomputed from
  tracking. The only relational measures are the NFL-computed columns in `player_play`.
- Tracking columns: `x, y, s, a, dis, o, dir`, and `event` (a play-event label such as
  `ball_snap`, `pass_forward`, `first_contact`, `tackle`; null on 93% of frames).
- `player_play` and tracking list nearly the same player-plays (314,197 vs 314,944; 2,497 in
  tracking only, 1,750 in `player_play` only, about 0.7% either way).
- **Scope of plays:** scrimmage plays only (no kicker, punter or long-snapper positions). Snaps split
  about 51/49 offense/defense. **WR and TE rows exist only on pass plays** (100% have a route
  and a pass result); OL, DL and DB rows include run plays (about 40% of their snaps). So there
  is no run-play sample for receivers.
- Season mix of player-plays: preseason 51,759 (16%), regular season 249,269, postseason 13,169.
  12,490 (4.0%) are on plays nullified by a penalty.

**Snaps per player (regular season).** 401 of 510 players have at least one regular-season snap;
**109 (21%) have none** (78 undrafted, 31 drafted).

| Position group | Players | Any snap | Median snaps | Career ≥500 | Rookie ≥100 | Rookie ≥250 | Rookie ≥500 |
|---|---|---|---|---|---|---|---|
| DB | 122 | 96 | 311 | 46 | 67 | 52 | 28 |
| OL | 121 | 91 | 328 | 51 | 59 | 53 | 39 |
| DL | 118 | 98 | 238 | 33 | 63 | 37 | 15 |
| WR | 107 | 83 | 187 | 29 | 52 | 30 | 5 |
| TE | 42 | 33 | 107 | 5 | 16 | 6 | 0 |

(*Median snaps* is the median over all players in the group, zeros included, summed across
seasons. *Career* = all seasons in the data, regular season only.) Rookie-season medians: DB 146, DL 133, WR 89, OL 89, TE 38 snaps. Overall the median
rookie has **102** regular-season snaps; 378 of 510 played at least one regular-season snap in their
rookie year (2023: 122, 2024: 131, 2025: 125). **Rookies with enough snaps to measure anything are
a minority**: 178 of 510 reach 250 rookie snaps.

**Cross-check against an independent source.** The NFL's own career totals in
`player_career_successes` agree: no player has more tracked snaps than career snaps, and the 105
players with 0 career scrimmage snaps are among the 109 with 0 tracked. Tracked snaps are **87% of
career snaps in the regular season and 92% with playoffs** (consistent across classes, 90-94%),
so career counts appear to include playoffs. About 8% of career snaps remain unexplained.
`career_games_active` includes special-teams-only games, which this dataset does not contain.

**Play context columns** (`player_play`, all about 100% filled): down, yards to go, quarter, game
clock, scores, win probability, yard line, play direction, EPA and expected points, offense
formation (98%), receiver alignment (98%), team coverage man/zone and type (88%), in-motion
(OL/WR/TE only).

**Outcome columns exist only for the roles they describe:**

| Group | Opportunity-type columns | Outcome columns (share of the group's snaps with a value) |
|---|---|---|
| WR / TE | `route_ran` (100%), `separation_at_pass_forward` (88%), `cushion` (95% / 79%) | `target` (100%), `rec_yards` and `yards_after_catch` (12%, only on catches), `expected_yards_after_catch` (about 17%) |
| OL | `pass_rushers_encountered`, `dropback_duration` (56%: pass plays) | `pressure_allowed`, `sack_allowed` (56%), `peak_pressure_probability_allowed` (53%), `time_to_pressure_allowed` (5%) |
| DL | `player_get_off` (63%), `blitzing` (55%) | `sack` (55%), `unblocked_pressure` (55%), `quick_pressure` (5%), `time_to_pressure` and `time_to_qb_hurry` (5%), `tackle`, `tackle_for_loss`, `caused_forced_fumble` (6%) |
| DB | `coverage_assignment` (49%), `cushion` (59%), `team_coverage_*` | `tackle`, `tackle_for_loss` (9%); **no outcome for the defender in coverage** (`target` is True for only 8 DB snaps) |

Common to all: `pass_result` (C/I/S/R/IN), `yards_gained`, `expected_points_added`, penalty fields.
Not present: run-block outcomes for OL, route-level outcomes for non-receivers, tracking-based
route or block metrics (those must be built from the 10 Hz data).

---

## 4. Linking Combine players to in-game players

**By ID: complete.** `nfl_id` is the only key and it works everywhere. All 510 players link across
`players`, `combine_results`, `player_career_successes` and `combine_tracking`. **Every ID in
`player_play` (497) and in the game tracking (497) is one of the 510: zero orphans.** The same 497
players appear in both. `players` and `combine_results` also agree on draft year (0 mismatches).

**Unmatched: 13 players (2.5%)**, all with 0 career offensive, defensive and special-teams snaps and
0 games active, per the NFL's own file, so these are real "never played" cases, not linking failures:
7 undrafted (3 TE, 1 OLB, 1 WR, 1 DE, 1 ILB), and 6 drafted in rounds 3-7 of 2025 who took no snap
(FS, TE, 2 CB, G, OLB). Nine of the 13 are from the 2025 class (6 drafted, 3 undrafted), the class
with only one season of games.

**Cautions**
- Two names are duplicated with different IDs ("Anthony Johnson", 2023 FS and CB; "Leonard Taylor",
  2023 TE and 2024 DT). **Never join on name.**
- `draft_overall_pick` repeats across years (222 distinct values for 383 drafted players); it is only
  unique within a draft year.
- A further 96 players have an ID in the game data but **zero regular-season snaps** (only preseason
  or playoff action), so "linked" does not mean "usable".

---

## 5. Missingness and quality

**Small tables: clean.** No impossible values; no duplicates in `players`, `combine_results` or
`games`. Ranges: 40-yard 4.28-5.48 s, 10-yd split 1.46-1.96 s, vertical 23-44 in, broad jump
93-138 in, 3-cone 6.57-8.19 s, shuttle 3.93-5.03 s, bench 8-39 reps, height 68.1-80.6 in, weight
154-374 lb, birth dates 1997-2004. The 10-yd split is always under half the 40 time.

| Column(s) | Missing | Reading |
|---|---|---|
| `forty` / `ten_yd_split` / `vertical` / `broad_jump` | 86 / 85 / 72 / 87 | skipped or hurt: about 14-17% |
| `three_cone` / `short_shuttle` / `bench_reps` | 330 / 309 / 318 | optional drills: **60-65% missing** |
| `draft_round`, `draft_overall_pick`, `draft_pick_within_round` | 127 each | exactly the undrafted players |
| `ngs_college_production_score`, `ngs_final_score` | 1 each | |
| Combine tracking, game tracking | 0 in every column | |

Missingness in the scalars is **not random**: it differs by position (for example only 25 of 122
DBs have a 3-cone) and by who chose to skip.

**Game tracking (22,654,290 rows): clean except for rare glitches.** No nulls, no duplicates,
10 Hz (all but 8 frame gaps are exactly 100 ms). 396 player-plays (0.13%) contain at least one bad
frame (speed above 12 yd/s: 98 frames, up to 16.9; |acceleration| above 12: 72 frames, up to 33.8;
a step above 1.5 yd: 395 frames). Glitches are isolated, typically one frame, and one player
(`nfl_id` 55922) has position jumps of 34-40 yards in three plays of one game. Easy to filter. 4,509
frames sit outside x 0-120 and 79,753 outside y 0-53.3; most are probably legitimate out-of-bounds
positions, not checked.

**`player_play`: gaps are mostly structural** (a column is filled only for the roles it describes,
see section 3), but note:
- **Missing-as-empty-string:** `pass_result` uses `''` (not null) for run plays (103,636 rows), so a null
  count understates its missingness.
- **Odd values:** `down = 0` on 961 rows; `yards_gained` ranges from -99 to 98; `sack` and
  `sack_allowed` take 0.5 (shared sacks); `target` is True for 4 OL and 8 DB; `blitzing` is True
  for 95% of DL pass-rush snaps, so it likely means "rushing the passer", not a true blitz (confirm
  before use); the column `visitor_team_win_probility_added` is misspelled in the source.
- **Light gaps:** `lined_up_position` 0.4% null, `yardline_side` 1.3%, `offense_formation` 1.7%.
- **Sparse columns:** `rush_yards` has 22 values and `fumble`/`fumble_lost` 73; unusable on
  their own. `time_to_pressure_allowed` is 4,970 rows and `quick_pressure` 3,763.
- `lined_up_position` is not the same as the listed position (see the hybrids in section 1).
- Duplicate (game, play, player) rows: 0 in both tracking and `player_play`.

---

## 6. Sample sizes by position group

All regular season. *Opportunity* = the snaps where the outcome could occur (definitions below).
"Rookie" columns use the draft-year season only.

**Table A: who is available**

| Group | Players | With reg. snaps | Reg. snaps | Opportunity | Opps | Median opps | ≥100 opps | ≥250 | ≥500 | Rookie ≥100 | Rookie ≥250 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DB | 122 | 96 | 66,916 | coverage snaps | 39,581 | 273 | 67 | 50 | 32 | 57 | 33 |
| DL | 118 | 98 | 52,609 | pass-rush snaps | 28,970 | 151 | 68 | 35 | 19 | 47 | 18 |
| OL | 121 | 91 | 86,582 | pass-block snaps | 48,698 | 433 | 66 | 54 | 41 | 56 | 44 |
| WR | 107 | 83 | 35,427 | routes run | 35,427 | 277 | 63 | 43 | 29 | 52 | 30 |
| TE | 42 | 33 | 7,735 | routes run | 7,735 | 183 | 21 | 11 | 5 | 16 | 6 |

**Table B: candidate outcome columns**

| Group | Outcome | Events | Rated per | Rate | Players ≥10 events | ≥5 events | Std. error of a rate at 250 |
|---|---|---|---|---|---|---|---|
| DB | tackles | 3,869 | snap | 5.8% | 67 | 77 | 1.5 pp |
| DB | tackles for loss | 212 | snap | 0.3% | 7 | 13 | 0.4 pp |
| DL | sacks | 396 | pass-rush snap | 1.4% | 13 | 26 | 0.7 pp |
| DL | unblocked pressures | 243 | pass-rush snap | 0.8% | 9 | 18 | 0.6 pp |
| DL | tackles for loss | 542 | snap | 1.0% | 17 | 35 | 0.6 pp |
| OL | pressures allowed | 4,104 | pass-block snap | 8.4% | 66 | 72 | 1.8 pp |
| OL | sacks allowed | 561 | pass-block snap | 1.2% | 21 | 43 | 0.7 pp |
| WR | targets | 6,513 | route | 18.4% | 67 | 71 | 2.5 pp |
| WR | receptions | 4,098 | route | 11.6% | 60 | 67 | 2.0 pp |
| TE | targets | 1,325 | route | 17.1% | 22 | 23 | 2.4 pp |
| TE | receptions | 941 | route | 12.2% | 20 | 23 | 2.1 pp |

**Definitions.** WR/TE opportunity = `route_ran` filled; OL = `pass_rushers_encountered` filled
(pass-block snap); DL = `sack` filled (pass-rush snap); DB = `coverage_assignment` filled. Tackles
and tackles for loss are rated per all snaps because they also happen on run plays. The standard
error is the binomial `sqrt(p(1-p)/n)` at n = 250: how much one player's measured rate wobbles from
chance alone. It ignores that opponents, teams and game situations differ.

**Reading the tables (facts, not a recommendation)**
- **DB** has the most players but its only in-data outcomes are tackles and tackles for loss; there is
  no target or completion-allowed for the defender in coverage.
- **DL** has plenty of pass-rush snaps (28,970) but rare events: only 13 players have 10+ sacks and 9
  have 10+ unblocked pressures. Rates per player are very noisy at typical snap counts.
- **OL** has the richest outcome (pressure allowed: 4,104 events, 66 players with 10+, 54 with 250+
  pass-block snaps), though its 8.4% rate still wobbles by about 1.8 points at 250 snaps.
- **WR** is large (63 players with 100+ routes) with frequent events. Relative noise at 250
  snaps: targets about 13% of the rate (2.5 points on 18.4%), OL pressures allowed about 21%
  (1.8 on 8.4%), DL sacks about 53% (0.7 on 1.4%), OL sacks allowed about 58% (0.7 on 1.2%).
- **TE** is small: 42 players, 21 with 100+ routes, 11 with 250+.
- Counting only **rookie** seasons roughly halves every group's usable sample.
- Players are **not independent rows**: the same player contributes many snaps, so any model must
  validate by player (grouped CV), as `CLAUDE.md` requires. Effective sample size is the number of
  players, about 20-70 per group, not the snap count.

---

## Surprises, in one list

1. Tracking contains only the 510 Combine players: no opponents, teammates or ball.
2. Only 3 draft classes; the 2025 class has one season of games.
3. 21% of players (109) never took a regular-season snap in the data.
4. No QB and almost no RB; no LB group; WR/TE appear only on pass plays.
5. Combine `dis` disagrees with positions and `s`; game-file `dis` is fine.
6. Sensor 40 times are 0.36 s slower than official, with a year-to-year drift, though correlated 0.91.
7. 3-cone/shuttle/bench are missing for about 60-65% of players, and not at random.
8. Defenders in coverage have no outcome column.
9. `pass_result` uses `''` for missing; `blitzing` likely means "pass-rushing".
10. 8% of career snaps are unexplained by the tracked data.

## Open questions (need Mike or the competition data dictionary)

- How were the 510 players selected, and why are QB, RB and LB missing?
- Why does Combine `dis` fall short of its stated definition (61% of path length)? How is
  `blitzing` defined? What does the NFL's 40 sensor clock start on?
- How are the `ngs_*` scores computed, and are they safe to use as features?
- Are the sprint phases at the end of OL and DB drills part of the drill?
- Why are about 8% of career snaps absent from `player_play`?
- How many very short (10-20 frame) 3-cone and shuttle traces are there?
- Are 4,509 off-field x values and 79,753 off-sideline y values really out of bounds?

---

# One-page summary (paste into the project chat)

**Data audit: Combine to NFL (BDB 2027). All numbers from `python -m bdb27.audit`.**

**Who is in it.** 510 Combine players from three draft classes (2023: 160, 2024: 177, 2025: 173);
127 (25%) went undrafted. By Combine group: DB 122, OL 121, DL 118, WR 107, TE 42. No QBs, 1 RB,
no LB group (OLBs sit under DL/DB). All IDs match across all 9 files with zero orphans, so linking
by `nfl_id` is exact. 13 players never appear in game data; the NFL's own career file shows 0 snaps
for each. Never join on name (two duplicate names).

**Combine data.** Scalar results exist for everyone, but only the 40-yard dash has broad coverage
(424 players; 418 with a sensor trace, 82%). 3-cone, shuttle and bench are missing for 60-65%, and
not at random. 10 Hz sensor traces exist for the 40, 3-cone, shuttle and 6 position-specific drill
sets (about 100-120 players each for DB/OL/WR/DL; TE about 40; LB 4). Vertical, broad jump and
bench have no traces. Sampling is exactly 10 Hz with no gaps; speeds are physically plausible.
Sensor 40 times correlate 0.91 with official times but run 0.36 s slower (clock definition).

**In-game data.** 22.7M tracking rows for 2023-25, but **only these 510 players are tracked**: no
opponents, teammates or ball. `player_play` adds context and NFL-computed outcomes by role: WR/TE
(routes, targets, separation, cushion), OL (pressures and sacks allowed), DL (sacks, pressures,
get-off, tackles for loss), DB (coverage assignment, tackles; **no coverage outcome**). WR/TE rows
are pass plays only.

**Sample size is the main constraint.** 109 players (21%) have no regular-season snap. The median
rookie has 102 regular-season snaps; only 178 players reach 250 rookie snaps (OL 53, DB 52, DL 37,
WR 30, TE 6). Players with 100+ opportunities: OL 66, DL 68, DB 67, WR 63, TE 21. Rare events are the
problem: only 13 players have 10+ sacks, while OL pressures allowed (4,104 events; 66 players with
10+) and WR targets (6,513; 67 players with 10+) are plentiful. Effective sample = players (about
20-70 per group), not snaps.

**Quality.** Small tables are clean. Game tracking has 0.13% glitch player-plays (isolated, easy to
filter). Watch: Combine `dis` is unreliable (use `s`, `x`, `y`); `pass_result` uses `''` for run
plays; `blitzing` likely means "pass-rushing"; 8% of career snaps are not in the data.

**Open.** Selection of the 510; definitions of `dis` and the 40 clock; whether OL/DB drill traces
include a sprint phase; short 3-cone/shuttle traces. No topic proposed.

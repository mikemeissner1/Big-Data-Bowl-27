"""Data audit tables (docs/research/data-audit.md).

Run ``uv run python -m bdb27.audit`` to print every table quoted in the audit as markdown.
Reads Parquet only. The three large game-tracking files are scanned lazily.

Conventions used throughout:
* "Position group" = ``combine_results.combine_position`` (DB, DL, OL, WR, TE).
* A "snap" is one ``player_play`` row (a scrimmage play the player was on the field for).
* "Regular season" = ``games.season_type == 'REG'``; "rookie season" = season == draft_year.
"""

from __future__ import annotations

import numpy as np
import polars as pl

from bdb27.paths import DATA_INTERIM as D

GROUPS = ["DB", "DL", "OL", "WR", "TE"]


def _scan(name: str) -> pl.LazyFrame:
    return pl.scan_parquet(D / f"{name}.parquet")


def players_table() -> pl.DataFrame:
    """One row per Combine player: position, draft year, draft status."""
    pls = pl.read_parquet(D / "players.parquet")
    cr = pl.read_parquet(D / "combine_results.parquet").select("nfl_id", "combine_position")
    return pls.join(cr, on="nfl_id").with_columns(
        pl.col("draft_round").is_null().alias("undrafted")
    )


def q1_players() -> dict[str, pl.DataFrame]:
    p = players_table()
    by_group_year = (
        p.group_by("combine_position", "draft_year")
        .len()
        .pivot(on="draft_year", index="combine_position", values="len")
        .join(p.group_by("combine_position").agg(pl.len().alias("total")), on="combine_position")
        .sort("total", descending=True)
    )
    by_nfl_pos = p.group_by("nfl_position").len().sort("len", descending=True)
    cr = pl.read_parquet(D / "combine_results.parquet")
    scalars = ["forty", "ten_yd_split", "vertical", "broad_jump", "three_cone", "short_shuttle"]
    scalars += ["bench_reps"]
    scalar_cov = (
        cr.group_by("combine_position")
        .agg(pl.len().alias("players"), *[pl.col(c).count().alias(c) for c in scalars])
        .sort("players", descending=True)
    )
    ct = _scan("combine_tracking").filter(pl.col("entity_type") == "PLAYER")
    std = ["FORTY_YARD_DASH", "THREE_CONE_DRILL", "SHORT_SHUTTLE"]
    sensor_cov = (
        ct.filter(pl.col("drill_type").is_in(std))
        .group_by("nfl_id", "drill_type")
        .len()
        .collect()
        .join(cr.select("nfl_id", "combine_position"), on="nfl_id")
        .group_by("combine_position", "drill_type")
        .agg(pl.col("nfl_id").n_unique().alias("players"))
        .pivot(on="drill_type", index="combine_position", values="players")
        .sort("combine_position")
    )
    drills = (
        ct.group_by("drill_type", "drill_name")
        .agg(
            pl.col("nfl_id").n_unique().alias("players"),
            pl.col("event_id").n_unique().alias("traces"),
            pl.len().alias("frames"),
        )
        .sort("drill_type", "drill_name")
        .collect()
    )
    return {
        "by_group_year": by_group_year,
        "by_nfl_position": by_nfl_pos,
        "scalar_coverage": scalar_cov,
        "sensor_coverage": sensor_cov,
        "drills": drills,
    }


def q2_forty_crosscheck() -> dict[str, float]:
    """Sensor-derived time to cover 40 yards from the first frame vs the official 40 time.

    Crude on purpose (start = first frame, straight-line distance, linear interpolation); it
    only asks whether sensor and official numbers move together.
    """
    f = (
        _scan("combine_tracking")
        .filter((pl.col("drill_name") == "FORTY_YARD_DASH") & (pl.col("entity_type") == "PLAYER"))
        .sort("event_id", "time")
        .select("event_id", "nfl_id", "x", "y")
        .collect()
    )
    rows = []
    for (_eid, pid), g in f.group_by(["event_id", "nfl_id"], maintain_order=True):
        x, y = g["x"].to_numpy(), g["y"].to_numpy()
        d = np.hypot(x - x[0], y - y[0])
        hit = np.where(d >= 40)[0]
        t40 = (
            ((hit[0] - 1) + (40 - d[hit[0] - 1]) / (d[hit[0]] - d[hit[0] - 1])) * 0.1
            if len(hit)
            else None
        )
        rows.append({"nfl_id": pid, "t40": t40})
    r = pl.DataFrame(rows, schema={"nfl_id": pl.Int64, "t40": pl.Float64})
    cr = pl.read_parquet(D / "combine_results.parquet").select("nfl_id", "forty")
    m = r.drop_nulls().join(cr.drop_nulls(), on="nfl_id")
    best = m.group_by("nfl_id").agg(pl.col("t40").min(), pl.col("forty").first())
    return {
        "traces": r.height,
        "traces_not_reaching_40yd": int(r["t40"].is_null().sum()),
        "mean_sensor_minus_official_s": float((m["t40"] - m["forty"]).mean()),
        "sd_sensor_minus_official_s": float((m["t40"] - m["forty"]).std()),
        "corr_best_attempt_vs_official": float(np.corrcoef(best["t40"], best["forty"])[0, 1]),
        "players_compared": best.height,
    }


def _player_play_enriched() -> pl.DataFrame:
    pp = pl.read_parquet(D / "player_play.parquet")
    games = pl.read_parquet(D / "games.parquet").select("game_id", "season", "season_type")
    return pp.join(games, on="game_id").join(
        players_table().select("nfl_id", "combine_position", "nfl_position", "draft_year"),
        on="nfl_id",
    )


def q3_snaps() -> dict[str, pl.DataFrame]:
    df = _player_play_enriched()
    reg = df.filter(pl.col("season_type") == "REG")
    per = reg.group_by("nfl_id", "season").agg(pl.len().alias("snaps"))
    base = players_table().select("nfl_id", "combine_position", "nfl_position", "draft_year")
    tot = per.group_by("nfl_id").agg(pl.col("snaps").sum().alias("reg_snaps"))
    rk = (
        per.join(base, on="nfl_id")
        .filter(pl.col("season") == pl.col("draft_year"))
        .select("nfl_id", pl.col("snaps").alias("rookie_snaps"))
    )
    t = (
        base.join(tot, on="nfl_id", how="left")
        .join(rk, on="nfl_id", how="left")
        .with_columns(pl.col("reg_snaps", "rookie_snaps").fill_null(0))
    )

    def summ(by: str) -> pl.DataFrame:
        return (
            t.group_by(by)
            .agg(
                pl.len().alias("players"),
                (pl.col("reg_snaps") > 0).sum().alias("any_reg_snap"),
                pl.col("reg_snaps").median().alias("median_reg_snaps"),
                (pl.col("reg_snaps") >= 500).sum().alias("career>=500"),
                (pl.col("rookie_snaps") >= 100).sum().alias("rookie>=100"),
                (pl.col("rookie_snaps") >= 250).sum().alias("rookie>=250"),
                (pl.col("rookie_snaps") >= 500).sum().alias("rookie>=500"),
            )
            .sort("players", descending=True)
        )

    return {
        "by_group": summ("combine_position"),
        "by_nfl_position": summ("nfl_position"),
        "players": t,
    }


def q3_career_check() -> dict[str, float]:
    """Tracked snaps vs the NFL's own career snap counts (independent source)."""
    df = _player_play_enriched()
    cs = pl.read_parquet(D / "player_career_successes.parquet").with_columns(
        (pl.col("career_offensive_snaps") + pl.col("career_defensive_snaps")).alias("career")
    )
    out = {}
    for label, types in [("reg", ["REG"]), ("reg_post", ["REG", "POST"])]:
        t = (
            df.filter(pl.col("season_type").is_in(types))
            .group_by("nfl_id")
            .agg(pl.len().alias("tr"))
        )
        c = cs.join(t, on="nfl_id", how="left").fill_null(0)
        out[f"tracked_over_career_{label}"] = float(c["tr"].sum() / c["career"].sum())
    return out


# Per-group definition of "opportunity" and "events" (see module docstring in the audit doc).
OPPS = {
    "WR": ("routes run", pl.col("route_ran").is_not_null(),
           {"targets": pl.col("target"), "receptions": pl.col("rec_yards").is_not_null()}),
    "TE": ("routes run", pl.col("route_ran").is_not_null(),
           {"targets": pl.col("target"), "receptions": pl.col("rec_yards").is_not_null()}),
    "OL": ("pass-block snaps", pl.col("pass_rushers_encountered").is_not_null(),
           {"pressures allowed": pl.col("pressure_allowed"),
            "sacks allowed": pl.col("sack_allowed") > 0}),
    "DL": ("pass-rush snaps", pl.col("sack").is_not_null(),
           {"sacks": pl.col("sack") > 0, "unblocked pressures": pl.col("unblocked_pressure"),
            "tackles for loss": pl.col("tackle_for_loss")}),
    "DB": ("coverage snaps", pl.col("coverage_assignment").is_not_null(),
           {"tackles": pl.col("tackle") == 1, "tackles for loss": pl.col("tackle_for_loss")}),
}  # fmt: skip


def q6_sample_sizes() -> dict[str, pl.DataFrame]:
    """Per position group: (A) players and opportunities, (B) outcome events and noise.

    Regular season only. ``rookie`` = the player's draft-year season.
    ``se_at_250`` is the binomial standard error of an event rate measured over 250
    opportunities, sqrt(p(1-p)/250): how noisy one player's rate would be.
    """
    df = _player_play_enriched().filter(pl.col("season_type") == "REG")
    n_players = players_table().group_by("combine_position").len()
    table_a, table_b = [], []
    for g in GROUPS:
        label, opp, events = OPPS[g]
        sub = df.filter(pl.col("combine_position") == g)
        per = sub.group_by("nfl_id", "season", "draft_year").agg(
            pl.len().alias("snaps"), opp.sum().alias("opps"),
            *[e.fill_null(False).sum().alias(n) for n, e in events.items()],
        )  # fmt: skip
        allyrs = per.group_by("nfl_id").agg(pl.all().exclude("season", "draft_year").sum())
        rookie = per.filter(pl.col("season") == pl.col("draft_year"))
        table_a.append(
            {
                "group": g,
                "players": int(n_players.filter(pl.col("combine_position") == g)["len"][0]),
                "with_reg_snaps": allyrs.height,
                "reg_snaps": int(allyrs["snaps"].sum()),
                "opportunity": label,
                "opps_total": int(allyrs["opps"].sum()),
                "median_opps": float(allyrs.filter(pl.col("opps") > 0)["opps"].median()),
                "players>=100": int((allyrs["opps"] >= 100).sum()),
                "players>=250": int((allyrs["opps"] >= 250).sum()),
                "players>=500": int((allyrs["opps"] >= 500).sum()),
                "rookie>=100": int((rookie["opps"] >= 100).sum()),
                "rookie>=250": int((rookie["opps"] >= 250).sum()),
            }
        )
        for n in events:
            tot = int(allyrs[n].sum())
            # Tackles happen on run plays too, so they are rated per snap, not per pass opportunity.
            per_snap = "tackle" in n
            denom = int(allyrs["snaps" if per_snap else "opps"].sum())
            rate = tot / denom
            table_b.append(
                {
                    "group": g,
                    "outcome": n,
                    "events": tot,
                    "per": "snap" if per_snap else label,
                    "rate": round(rate, 4),
                    "players>=10_events": int((allyrs[n] >= 10).sum()),
                    "players>=5_events": int((allyrs[n] >= 5).sum()),
                    "se_at_250": round((rate * (1 - rate) / 250) ** 0.5, 4),
                }
            )
    return {"A_opportunities": pl.DataFrame(table_a), "B_events": pl.DataFrame(table_b)}


def main() -> None:
    pl.Config.set_tbl_formatting("ASCII_MARKDOWN")
    pl.Config.set_tbl_rows(100)
    pl.Config.set_tbl_cols(30)
    pl.Config.set_tbl_width_chars(250)
    pl.Config.set_tbl_hide_dataframe_shape(True)
    pl.Config.set_tbl_hide_column_data_types(True)
    for name, t in q1_players().items():
        print(f"\n### Q1 {name}\n{t}")
    print("\n### Q2 forty cross-check\n", q2_forty_crosscheck())
    snaps = q3_snaps()
    print("\n### Q3 snaps by group\n", snaps["by_group"])
    print("\n### Q3 snaps by nfl_position\n", snaps["by_nfl_position"])
    print("\n### Q3 career check\n", q3_career_check())
    for name, t in q6_sample_sizes().items():
        print(f"\n### Q6 {name} (regular season)\n{t}")


if __name__ == "__main__":
    main()

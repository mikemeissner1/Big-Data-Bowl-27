"""Figures for the data audit (docs/research/data-audit.md).

Every figure in the audit is generated here, from the Parquet files in ``data/interim``,
and saved to ``reports/figures/``. Nothing is hand-drawn.

Example players are chosen by a deterministic rule (no randomness): among players of a
position group who have both a 40-yard-dash trace and the chosen position drill, take the
one whose official 40 time is closest to that group's median.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # draw to files only; no window needed
import matplotlib.pyplot as plt
import polars as pl

from bdb27.paths import DATA_INTERIM, FIGURES

# Validated default categorical palette (dataviz skill), slots 1-3, light surface.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
COLORS = {"WR": "#2a78d6", "OL": "#eb6834", "DB": "#1baf7a"}

# (combine position group, position-specific drill, pretty drill name)
EXAMPLES = [
    ("WR", "SLANT_ROUTE_LEFT", "WR: slant route"),
    ("OL", "FIVE_YARD_WAVE_DRILL_SLIDE_AND_SHUFFLE", "OL: 5-yard wave (slide and shuffle)"),
    ("DB", "W_DRILL", "DB: W-drill"),
]


def _style(ax: plt.Axes) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK_2)
        ax.spines[side].set_linewidth(0.8)
    ax.grid(color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK_2, labelsize=9)
    ax.xaxis.label.set_color(INK_2)
    ax.yaxis.label.set_color(INK_2)


def pick_examples() -> list[dict]:
    """Choose one typical player per example position (see module docstring)."""
    res = pl.read_parquet(DATA_INTERIM / "combine_results.parquet")
    ct = pl.scan_parquet(DATA_INTERIM / "combine_tracking.parquet").filter(
        pl.col("entity_type") == "PLAYER"
    )
    has_forty = (
        ct.filter(pl.col("drill_name") == "FORTY_YARD_DASH").select("nfl_id").unique().collect()
    )
    picks = []
    for group, drill, label in EXAMPLES:
        has_drill = ct.filter(pl.col("drill_name") == drill).select("nfl_id").unique().collect()
        pool = res.filter(
            (pl.col("combine_position") == group)
            & pl.col("forty").is_not_null()
            & pl.col("nfl_id").is_in(has_forty["nfl_id"].implode())
            & pl.col("nfl_id").is_in(has_drill["nfl_id"].implode())
        )
        med = res.filter(pl.col("combine_position") == group)["forty"].median()
        row = (
            pool.with_columns((pl.col("forty") - med).abs().alias("gap"))
            .sort("gap", "nfl_id")  # nfl_id breaks ties deterministically
            .row(0, named=True)
        )
        picks.append(
            {
                "group": group,
                "drill": drill,
                "label": label,
                "nfl_id": row["nfl_id"],
                "forty": row["forty"],
                "weight": row["combine_weight"],
            }
        )
    return picks


def _trace(nfl_id: int, drill: str, best: str | None = None) -> pl.DataFrame:
    """One attempt of one drill for one player: the lowest attempt number, or the attempt
    with the highest peak speed when ``best == 'speed'``. Adds ``t`` (seconds from first frame)."""
    df = (
        pl.scan_parquet(DATA_INTERIM / "combine_tracking.parquet")
        .filter(
            (pl.col("nfl_id") == nfl_id)
            & (pl.col("drill_name") == drill)
            & (pl.col("entity_type") == "PLAYER")
        )
        .sort("time")
        .collect()
    )
    if best == "speed":
        attempt = (
            df.group_by("attempt").agg(pl.col("s").max()).sort("s", descending=True)["attempt"][0]
        )
    else:
        attempt = df["attempt"].min()
    df = df.filter(pl.col("attempt") == attempt)
    t0 = df["time"].min()
    return df.with_columns(((pl.col("time") - t0).dt.total_milliseconds() / 1000).alias("t"))


def fig_forty_speed(picks: list[dict]):
    """Speed vs time in the 40-yard dash for the three example players."""
    fig, ax = plt.subplots(figsize=(8, 4.6), facecolor=SURFACE)
    _style(ax)
    for p in picks:
        tr = _trace(p["nfl_id"], "FORTY_YARD_DASH", best="speed")
        c = COLORS[p["group"]]
        ax.plot(tr["t"], tr["s"], color=c, linewidth=2, marker="o", markersize=3, zorder=3)
        ax.annotate(
            f"{p['group']}  (official 40: {p['forty']:.2f} s)",
            xy=(tr["t"][-1], tr["s"][-1]),
            xytext=(6, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            color=INK,
        )
    ax.set_xlabel("Seconds since the first sensor frame")
    ax.set_ylabel("Speed (yards per second)")
    ax.set_xlim(0, 7.6)
    ax.set_title(
        "40-yard dash: three typical players, one dot per 10 Hz sensor frame",
        loc="left",
        fontsize=11,
        color=INK,
    )
    fig.tight_layout()
    return fig


def fig_drill_paths(picks: list[dict]):
    """Field-position path (x, y in yards) in one position-specific drill per example player."""
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.2), facecolor=SURFACE)
    for ax, p in zip(axes, picks, strict=True):
        _style(ax)
        tr = _trace(p["nfl_id"], p["drill"])
        c = COLORS[p["group"]]
        ax.plot(tr["x"], tr["y"], color=c, linewidth=2, zorder=3)
        ax.scatter(
            tr["x"][0], tr["y"][0], s=40, color=c, edgecolor=SURFACE, linewidth=1.5, zorder=4
        )
        ax.scatter(
            tr["x"][-1], tr["y"][-1], s=40, color=INK, marker="s", edgecolor=SURFACE,
            linewidth=1.5, zorder=4,
        )  # fmt: skip
        ax.set_aspect("equal", adjustable="datalim")
        ax.set_title(p["label"], loc="left", fontsize=10, color=INK)
        ax.set_xlabel("x (yards, along the field)")
        ax.set_ylabel("y (yards, across the field)")
    fig.suptitle(
        "Position drills: path on the field (circle = start, square = end)",
        x=0.01,
        ha="left",
        fontsize=11,
        color=INK,
    )
    fig.tight_layout()
    return fig


def make_all() -> list[dict]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    picks = pick_examples()
    for name, fig in [
        ("audit_combine_40_speed.png", fig_forty_speed(picks)),
        ("audit_combine_drill_paths.png", fig_drill_paths(picks)),
    ]:
        fig.savefig(FIGURES / name, dpi=200, facecolor=SURFACE)
        plt.close(fig)
    return picks


if __name__ == "__main__":
    for p in make_all():
        print(p)

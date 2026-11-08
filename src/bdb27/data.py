"""Data loading: convert raw competition CSVs to Parquet (no analysis here).

Why Parquet: it is compressed, typed and column-oriented, so the large tracking
files load in a fraction of the time and memory of CSV (important on an 18 GB laptop).

Raw files in ``data/raw`` are read-only inputs and are never modified or committed.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from bdb27.paths import DATA_INTERIM, DATA_RAW


def csv_to_parquet(csv_path: Path, out_dir: Path = DATA_INTERIM, overwrite: bool = False) -> Path:
    """Stream one CSV into a Parquet file of the same name; return the output path.

    Uses polars' lazy ``scan_csv`` + ``sink_parquet`` so the whole file is never
    held in memory at once.
    """
    csv_path = Path(csv_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{csv_path.stem}.parquet"
    if out_path.exists() and not overwrite:
        return out_path
    # infer_schema_length=10_000 is a compromise; check dtypes after conversion.
    pl.scan_csv(csv_path, infer_schema_length=10_000).sink_parquet(out_path)
    return out_path


def convert_all(
    raw_dir: Path = DATA_RAW, out_dir: Path = DATA_INTERIM, overwrite: bool = False
) -> list[Path]:
    """Convert every ``*.csv`` in ``raw_dir`` to Parquet in ``out_dir``."""
    csvs = sorted(Path(raw_dir).glob("*.csv"))
    if not csvs:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")
    return [csv_to_parquet(p, out_dir, overwrite) for p in csvs]


if __name__ == "__main__":
    for path in convert_all():
        print(path)

"""Project folder locations, so no code hard-codes a path on one machine."""

from pathlib import Path

# src/bdb27/paths.py -> repo root is three levels up
ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_INTERIM = ROOT / "data" / "interim"
DATA_PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "reports" / "figures"

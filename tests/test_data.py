import polars as pl

import bdb27
from bdb27.data import convert_all, csv_to_parquet


def test_package_imports():
    assert bdb27.__version__


def test_csv_to_parquet_roundtrip(tmp_path):
    csv = tmp_path / "toy.csv"
    csv.write_text("a,b\n1,x\n2,y\n")
    out = csv_to_parquet(csv, tmp_path / "interim")
    assert out.exists()
    assert pl.read_parquet(out).to_dicts() == [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]


def test_convert_all_requires_csvs(tmp_path):
    try:
        convert_all(tmp_path, tmp_path / "out")
    except FileNotFoundError:
        return
    raise AssertionError("expected FileNotFoundError")

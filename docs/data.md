# Data

The competition CSVs live in `data/raw/` on Mike's Mac (about 2.3 GB, 9 files, from Kaggle).

- **Never commit anything in `data/`.** The whole folder is gitignored.
- Treat `data/raw/` as read-only. Do not re-download; do not edit.
- `data/interim/` holds Parquet conversions (`uv run python -m bdb27.data`).
- `data/processed/` holds analysis-ready tables derived from interim.
- Because the folders are ignored, they do not exist in a fresh clone; `make setup` creates them.
- Kaggle notebooks read the data from Kaggle's own input path, not from here.

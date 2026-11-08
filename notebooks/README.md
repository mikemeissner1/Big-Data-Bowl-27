# Notebooks

Notebooks are for **exploration**. Anything reusable (loading, features, models, plotting
helpers) moves into `src/bdb27/` and is imported, so it can be tested and reused.

## How notebooks work with git and Claude

Each notebook is a **pair**: `name.ipynb` (what Jupyter opens) and `name.py` (plain text).
[jupytext](https://jupytext.readthedocs.io) keeps the two in sync using the *percent* format:

```python
# %% [markdown]
# ## A markdown cell

# %%
import polars as pl  # a code cell
```

- **Commit the `.py`**; `.ipynb` files are gitignored (their JSON and embedded outputs make
  diffs unreadable).
- **Claude can read and edit the `.py` file** like any other code. Jupytext syncs the changes
  into the `.ipynb` the next time you open it in JupyterLab (or run `make sync`).
- Run cells yourself in JupyterLab to see output. Paste anything surprising to Claude, or save
  figures to `reports/figures/` from code.

## Create or sync

`notebooks/jupytext.toml` auto-pairs every notebook, so in JupyterLab you just create a notebook and a matching `.py` appears when you save. Manual commands:

```bash
uv run jupytext --set-formats ipynb,py:percent notebooks/01_explore.ipynb   # pair an existing notebook
uv run jupytext --to ipynb notebooks/01_explore.py                          # make an .ipynb from a .py
uv run jupytext --sync notebooks/*.py                                       # sync both directions
```

Naming: `NN_short_topic.py` (e.g. `01_data_audit.py`). Always load data from `data/interim`
Parquet via `bdb27.paths`, never from an absolute path.

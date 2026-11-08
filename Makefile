.PHONY: setup lint format test lab sync

setup:      ## Create .venv and install pinned dependencies
	uv sync
	mkdir -p data/raw data/interim data/processed

lint:       ## Check style and common bugs
	uv run ruff check .
	uv run ruff format --check .

format:     ## Auto-format code
	uv run ruff check --fix .
	uv run ruff format .

test:       ## Run tests
	uv run pytest

lab:        ## Open JupyterLab
	uv run jupyter lab

sync:       ## Sync notebooks/*.py with their .ipynb pairs
	uv run jupytext --sync notebooks/*.py

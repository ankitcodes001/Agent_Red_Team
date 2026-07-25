.PHONY: install fmt lint type test check run clean

install:      ## Create venv and install with dev extras
	uv sync --extra dev

fmt:          ## Auto-format
	uv run ruff format src tests

lint:         ## Lint
	uv run ruff check src tests

type:         ## Type-check
	uv run mypy src

test:         ## Run tests
	uv run pytest

check: lint type test  ## Lint + type + test

run:          ## Run a demo campaign against the bundled target
	uv run redteam run --target examples/demo --config examples/redteam.yaml

clean:
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache scorecard.html runs

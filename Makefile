.PHONY: install run clean

install:
	uv sync

run:
	uv run python -m src.main

clean:
	rm -rf .venv __pycache__ src/__pycache__ tests/__pycache__
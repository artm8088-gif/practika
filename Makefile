.PHONY: install run clean demo errors

install:
	uv sync

run:
	uv run python -m src.main

demo:
	uv run python -m src.main --vfs ./vfs --script ./scripts/demo.txt

errors:
	uv run python -m src.main --vfs ./vfs --script ./scripts/errors.txt

clean:
	rm -rf .venv __pycache__ src/__pycache__ tests/__pycache__
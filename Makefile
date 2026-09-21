.PHONY: install run demo errors full-test minimal files nested clean

install:
	uv sync

run:
	uv run python -m src.main

demo:
	uv run python -m src.main --vfs ./vfs/minimal.csv --script ./scripts/demo.txt

errors:
	uv run python -m src.main --vfs ./vfs/minimal.csv --script ./scripts/errors.txt

full-test:
	uv run python -m src.main --vfs ./vfs/nested.csv --script ./scripts/full_test.txt

minimal:
	uv run python -m src.main --vfs ./vfs/minimal.csv

files:
	uv run python -m src.main --vfs ./vfs/files.csv

nested:
	uv run python -m src.main --vfs ./vfs/nested.csv

clean:
	rm -rf .venv __pycache__ src/__pycache__ tests/__pycache__
.PHONY: install run demo errors minimal files nested full-test stage4 clean

install:
	uv sync

run:
	uv run python -m src.main

demo:
	uv run python -m src.main --vfs ./vfs/minimal.csv --script ./scripts/demo.txt

errors:
	uv run python -m src.main --vfs ./vfs/minimal.csv --script ./scripts/errors.txt

minimal:
	uv run python -m src.main --vfs ./vfs/minimal.csv

files:
	uv run python -m src.main --vfs ./vfs/files.csv

nested:
	uv run python -m src.main --vfs ./vfs/nested.csv

full-test:
	uv run python -m src.main --vfs ./vfs/nested.csv --script ./scripts/full_test.txt

stage4:
	uv run python -m src.main --vfs ./vfs/nested.csv --script ./scripts/stage4_test.txt

clean:
	rm -rf .venv __pycache__ src/__pycache__ tests/__pycache__
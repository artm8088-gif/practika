.PHONY: install run clean demo errors stage3

install:
	uv sync

run:
	uv run python -m src.main

demo:
	uv run python -m src.main --vfs ./vfs/minimal.csv --script ./scripts/demo.txt

errors:
	uv run python -m src.main --vfs ./vfs/minimal.csv --script ./scripts/errors.txt

stage3:
	uv run python -m src.main --vfs ./vfs/nested.csv --script ./scripts/full_test.txt

stage4:
	uv run python -m src.main --vfs ./vfs/nested.csv --script ./scripts/stage4_test.txt

stage5:
	uv run python -m src.main --vfs ./vfs/nested.csv --script ./scripts/stage5_test.txt

clean:
	rm -rf .venv __pycache__ src/__pycache__ tests/__pycache__
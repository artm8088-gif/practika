#!/usr/bin/env bash
# Запуск с VFS, где ≥3 уровней вложенности.
set -e
cd "$(dirname "$0")/.."
uv run python -m src.main --vfs ./vfs/nested.csv --script ./scripts/full_test.txt
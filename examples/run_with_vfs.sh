#!/usr/bin/env bash
# Запуск с явно указанным путём к VFS.
set -e
cd "$(dirname "$0")/.."
uv run python -m src.main --vfs ./vfs
#!/usr/bin/env bash
# Запуск с явно указанным CSV-файлом VFS.
set -e
cd "$(dirname "$0")/.."
uv run python -m src.main --vfs ./vfs/nested.csv
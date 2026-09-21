#!/usr/bin/env bash
# Запуск с минимальным VFS.
set -e
cd "$(dirname "$0")/.."
uv run python -m src.main --vfs ./vfs/minimal.csv
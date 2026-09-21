#!/usr/bin/env bash
# Запуск с VFS из нескольких файлов.
set -e
cd "$(dirname "$0")/.."
uv run python -m src.main --vfs ./vfs/files.csv
#!/usr/bin/env bash
# Запуск с VFS и стартовым скриптом.
set -e
cd "$(dirname "$0")/.."
uv run python -m src.main --vfs ./vfs --script ./scripts/demo.txt
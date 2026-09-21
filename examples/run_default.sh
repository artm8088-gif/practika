#!/usr/bin/env bash
# Запуск с настройками по умолчанию.
set -e
cd "$(dirname "$0")/.."
uv run python -m src.main
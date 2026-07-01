#!/usr/bin/env bash
# Seed personas *_test_2 sur baseline B (sqlite_test) — relançable.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACK="$ROOT/hugo_back"
export DJANGO_SETTINGS_MODULE=config.settings.sqlite_test
export HUGO_P0_V17_ENABLED=false
PY="$BACK/.venv/bin/python"

cd "$BACK"
"$PY" manage.py migrate --run-syncdb
"$PY" manage.py bootstrap_personas_test_2 --write-fixtures

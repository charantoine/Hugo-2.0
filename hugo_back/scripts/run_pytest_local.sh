#!/usr/bin/env bash
# Baseline B smoke — toujours via l'interpréteur du venv (évite pytest → Python 3.12 parasite).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.sqlite_test}"
export HUGO_P0_V17_ENABLED="${HUGO_P0_V17_ENABLED:-false}"
PY="${ROOT}/.venv/bin/python"

if [[ ! -x "$PY" ]]; then
  echo "venv manquant : python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

exec "$PY" -m pytest "$@"

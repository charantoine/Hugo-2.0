#!/usr/bin/env bash
# Suite reconfiguration chats tuteur/formateur (baseline B, P0 legacy).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.sqlite_test}"
export HUGO_P0_V17_ENABLED=false
exec "${ROOT}/.venv/bin/python" -m pytest apps/hugo/tests/test_chats_reconf_morning_baseline_b.py -v "$@"

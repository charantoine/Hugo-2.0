#!/usr/bin/env bash
# Encoors preprod oracle — JSON consolidé (M1, EVAL1, O1, OBS_BASE, D9BIS)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WS="$(cd "$ROOT/.." && pwd)"
OUT="${ENCOORS_ORACLE_OUT:-$WS/docs-workspace/encoors_oracle_preprod.generated.json}"

export ENCOORS_BASE_URL="${ENCOORS_BASE_URL:-https://hugoback.encoors.com}"
export ENCOORS_ORACLE_OUT="$OUT"

cd "$ROOT"
python3 scripts/encoors_oracle.py

echo ""
echo "Oracle JSON written to: $OUT"
if [[ -z "${ENCOORS_USERNAME:-}" || -z "${ENCOORS_PASSWORD:-}" ]]; then
  echo "NOTE: ENCOORS_USERNAME/PASSWORD not set — only unauthenticated probes executed (A_VÉRIFIER)."
fi

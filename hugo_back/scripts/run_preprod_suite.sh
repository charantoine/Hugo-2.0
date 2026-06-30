#!/usr/bin/env bash
# Hugo preprod — séquence tests backend + instructions Playwright/Encoors
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WS="$(cd "$ROOT/.." && pwd)"
cd "$ROOT"

if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.test}"

echo "=== Hugo preprod — backend pytest (noyau) ==="

PYTEST_FILES=(
  apps/hugo/tests/test_cluster3_oracles.py
  apps/hugo/tests/test_cluster4_surface_contracts.py
  apps/hugo/tests/test_session_memory_contract.py
  apps/hugo/tests/test_memory_summary_smoke.py
  apps/hugo/tests/test_evaluation_trace_minimal.py
  apps/hugo/tests/test_cta_synthesis_contract.py
  apps/hugo/tests/test_cta_evaluation_contract.py
  apps/hugo/tests/test_rag_support_tracing.py
  apps/hugo/tests/test_preprod_garde_fou.py
  apps/hugo/tests/test_observabilite_base.py
  apps/hugo/tests/test_analytics_absence_ui_exports.py
  apps/hugo/tests/test_d2_m07_confidentiality_oracles.py
  apps/hugo/tests/test_d2_m06_d2_m11_exports_and_analytics.py
  apps/hugo/tests/test_encadrants_role_guards.py
  apps/hugo/tests/test_rls_postgres_minimal.py
  apps/hugo/tests/test_vague5_e2e_scenarios.py
  apps/hugo/tests/test_posture_modes.py
  apps/hugo/tests/test_phase_progression.py
)

python -m pytest "${PYTEST_FILES[@]}" -q "$@"

echo ""
echo "=== Playwright (manual step) ==="
echo "  cd \"$WS/hugo-hugolucia/frontend_1.8\""
echo "  cd \"$ROOT\" && python manage.py bootstrap_smoke_playwright"
echo "  VITE_API_URL=/api npm run test:smoke"
echo ""
echo "=== Encoors oracle (optional, credentials required) ==="
echo "  export ENCOORS_USERNAME=... ENCOORS_PASSWORD=..."
echo "  ENCOORS_ORACLE_OUT=\"$WS/docs-workspace/encoors_oracle_preprod.generated.json\" python scripts/encoors_oracle.py"
echo ""
echo "=== RLS prod SQL (optional) ==="
echo "  psql -U <ROLE_APPLICATIF> -d <DB_PROD> -f scripts/audit_rls_prod_template.sql"
echo ""
echo "Backend preprod suite: PASS"

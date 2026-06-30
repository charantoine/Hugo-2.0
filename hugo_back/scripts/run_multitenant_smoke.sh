#!/usr/bin/env bash
# Multi-tenant smoke — backend tenant campaign + RLS gate + Playwright (optional).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WS="$(cd "$ROOT/.." && pwd)"
FE="$WS/hugo-hugolucia/frontend_1.8"

cd "$ROOT"
if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.test}"
export HUGO_RLS_STRICT="${HUGO_RLS_STRICT:-1}"

DB_NAME="${TEST_DB_NAME:-hugo_poc_test}"
if command -v psql >/dev/null 2>&1; then
  echo "=== RLS app role setup (if postgres available) ==="
  psql -U "${TEST_DB_USER:-postgres}" -d "$DB_NAME" -f scripts/setup_rls_app_role.sql 2>/dev/null || \
    echo "WARN: setup_rls_app_role.sql skipped (DB or role unavailable)"
fi

echo "=== Backend multi-tenant smoke (HUGO_RLS_STRICT=$HUGO_RLS_STRICT) ==="

PYTEST_FILES=(
  apps/accounts/tests/test_tenant_isolation.py
  apps/accounts/tests/test_tenant_campaign.py
  apps/referentials/tests/test_tutor_links_permissions.py
  apps/referentials/tests/test_group_visibility_by_tutor_links.py
  apps/hugo/tests/test_tutor_access_control.py
  apps/hugo/tests/test_encadrants_role_guards.py
  apps/hugo/tests/test_d2_m07_confidentiality_oracles.py
  apps/hugo/tests/test_cluster3_oracles.py
  apps/hugo/tests/test_d2_m06_d2_m11_exports_and_analytics.py
  apps/hugo/tests/test_rls_postgres_minimal.py
  tests/test_cross_tenant.py
)

python -m pytest "${PYTEST_FILES[@]}" -q "$@"

if [[ "${RUN_PLAYWRIGHT_SMOKE:-0}" == "1" ]]; then
  echo "=== Bootstrap tenant fixtures ==="
  python manage.py bootstrap_multitenant_smoke
  echo "=== Playwright multi-tenant e2e ==="
  cd "$FE"
  export SMOKE_RUN_TENANT=1
  npm run test:smoke -- tests_playwright/e2e/tenant_*.spec.ts
fi

echo "Multi-tenant smoke: PASS"

#!/usr/bin/env bash
# Affiche la stack Hugo locale attendue (settings + base) sans démarrer le serveur.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACK="$ROOT/hugo_back"
PY="$BACK/.venv/bin/python"

if [[ ! -x "$PY" ]]; then
  echo "venv introuvable : $PY"
  exit 1
fi

echo "=== Stack dev (postgres hugo_poc) ==="
(cd "$BACK" && DJANGO_SETTINGS_MODULE=config.settings.dev "$PY" manage.py print_runtime_stack)

echo ""
echo "=== Stack smoke (sqlite test.sqlite3) ==="
(cd "$BACK" && DJANGO_SETTINGS_MODULE=config.settings.sqlite_test "$PY" manage.py print_runtime_stack)

cat <<'EOF'

Référence :
  - Dev / campagne OF_test_2 : config.settings.dev → postgres hugo_poc
  - run_local_hugo.sh        : config.settings.sqlite_test → test.sqlite3 + bootstrap_smoke_playwright
  - Playwright E2E           : npm run test:e2e (depuis frontend_1.8)
EOF

#!/usr/bin/env bash
# Baseline B locale : backend hugo_back (sqlite_test) + front 1.8 via proxy /api → :8000
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACK="$ROOT/hugo_back"
FRONT="$ROOT/hugo-hugolucia/frontend_1.8"
LOG_DIR="$ROOT/.local-hugo-logs"
mkdir -p "$LOG_DIR"

export DJANGO_SETTINGS_MODULE=config.settings.sqlite_test
PY="$BACK/.venv/bin/python"
PIP="$BACK/.venv/bin/pip"

echo "==> Stack locale : SQLITE (config.settings.sqlite_test) — distincte de hugo_poc (dev postgres)"

if [[ ! -x "$PY" ]]; then
  echo "Création du venv dans hugo_back/.venv …"
  python3 -m venv "$BACK/.venv"
  "$PIP" install -r "$BACK/requirements.txt"
fi

ensure_sqlite_smoke_schema() {
  local db_file="$BACK/test.sqlite3"
  if [[ ! -f "$db_file" ]]; then
    return 0
  fi
  if ! "$PY" - <<'PY' 2>/dev/null
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.sqlite_test")
django.setup()
from django.db import connection

with connection.cursor() as cursor:
    if connection.vendor != "sqlite":
        raise SystemExit(0)
    description = connection.introspection.get_table_description(cursor, "trainer_knowledge_item")
    columns = {col.name for col in description}
    if "meta" not in columns:
        raise SystemExit(1)
PY
  then
    echo "    SQLite smoke obsolète (schéma trainer_knowledge_item) — régénération de test.sqlite3"
    rm -f "$db_file"
  fi
}

echo "==> Migrations + fixtures smoke"
cd "$BACK"
ensure_sqlite_smoke_schema
"$PY" manage.py print_runtime_stack
"$PY" manage.py migrate --run-syncdb
"$PY" manage.py ensure_sqlite_persona_schema
"$PY" manage.py bootstrap_smoke_playwright
"$PY" manage.py bootstrap_profile_migration_smoke

echo "==> Backend :8000 (log: $LOG_DIR/backend.log)"
if lsof -ti:8000 >/dev/null 2>&1; then
  echo "    Port 8000 déjà utilisé — on garde le process existant."
else
  nohup "$PY" manage.py runserver 8000 >"$LOG_DIR/backend.log" 2>&1 &
  echo $! >"$LOG_DIR/backend.pid"
fi

for i in {1..30}; do
  if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/auth/login/ | grep -qE '405|200'; then
    echo "    Backend OK sur http://127.0.0.1:8000"
    break
  fi
  sleep 1
  if [[ $i -eq 30 ]]; then
    echo "    ERREUR: backend ne répond pas. Voir $LOG_DIR/backend.log"
    exit 1
  fi
done

echo "==> Front Vite :5173 (log: $LOG_DIR/frontend.log)"
cd "$FRONT"
if [[ ! -d node_modules ]]; then
  npm install
fi

if lsof -ti:5173 >/dev/null 2>&1; then
  echo "    Port 5173 déjà utilisé — on garde le process existant."
else
  # /api → proxy Vite → http://localhost:8000 (évite Encoors dans .env.development)
  nohup env VITE_API_URL=/api npm run dev -- --port 5173 --strictPort >"$LOG_DIR/frontend.log" 2>&1 &
  echo $! >"$LOG_DIR/frontend.pid"
fi

APP_URL="http://localhost:5173/app"
for i in {1..40}; do
  if curl -s -o /dev/null -w "%{http_code}" "$APP_URL" | grep -qE '200|304'; then
    echo "    Front OK sur $APP_URL"
    break
  fi
  sleep 1
  if [[ $i -eq 40 ]]; then
    echo "    ERREUR: front ne répond pas. Voir $LOG_DIR/frontend.log"
    exit 1
  fi
done

echo "==> Ouverture Firefox : $APP_URL"
if [[ "$(uname -s)" == "Darwin" ]]; then
  open -a "Firefox" "$APP_URL" 2>/dev/null || open -a "Firefox Developer Edition" "$APP_URL" 2>/dev/null || /Applications/Firefox.app/Contents/MacOS/firefox "$APP_URL" &
elif command -v firefox >/dev/null 2>&1; then
  firefox "$APP_URL" &
else
  echo "Firefox introuvable. Ouvre manuellement : $APP_URL"
fi

cat <<EOF

Stack locale démarrée.
  Backend  : http://127.0.0.1:8000
  Front    : $APP_URL
  Login    : smoke_learner / smoke-pass-2026
  Logs     : $LOG_DIR/

Arrêt :
  kill \$(cat $LOG_DIR/backend.pid 2>/dev/null) \$(cat $LOG_DIR/frontend.pid 2>/dev/null) 2>/dev/null || true

Pytest local (baseline B sqlite) :
  cd hugo_back && ./scripts/run_pytest_local.sh apps/hugo/tests/test_trainer_*.py
EOF

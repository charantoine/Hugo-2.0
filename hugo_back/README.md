# Backend POC Hugo

Django multi-tenant backend for the AFEST reflective assistant (SPEC_POC_v1.4).

## Setup

- Python 3.7+
- PostgreSQL 15+ (RLS + pgvector optional)
- Redis (for Celery broker, optional for POC)

```bash
pip install -r requirements.txt
export DATABASE_URL=postgresql://user:pass@localhost:5432/hugo_poc
export SECRET_KEY=your-secret-key
python manage.py migrate
python manage.py runserver
```

## Tests

```bash
export TEST_DB_NAME=hugo_poc_test
pytest
```

Cross-tenant tests require RLS migrations to be applied on the test DB.

## Main endpoints

- `POST /auth/login/` — JWT login
- `GET /auth/me/` — current user
- `POST /admin/organisations/`, `POST /admin/users/` — admin (POC manual)
- `POST|GET /groups/`, `.../members/`, `.../tutor-links/`, `.../referential-config/`, `.../library/`
- `POST|GET /hugo/sessions/`, `.../messages/`, `.../generate-trace/`, `.../share/`
- `POST /traces/{id}/validate/`
- `GET /learners/sessions|traces|evidence/`
- `GET /dashboard/groups/{id}/learners/`, `.../timeline/`, `.../competences/`
- `POST /evidence/`
- `POST /documents/`, `POST /documents/{id}/index/`
- `POST /referentials/import-v2/`
- `POST /exports/run/`, `GET /exports/download/{run_id}/`
- `POST /quality/qualiopi/evidence-bundle/`

## Deploy (S0 — docker-compose)

From repo root:

```bash
cp .env.example .env
# Edit .env: set POSTGRES_PASSWORD, SECRET_KEY
docker compose up -d postgres redis minio
docker compose run --rm api python manage.py migrate
docker compose run --rm api python manage.py createsuperuser
docker compose up -d api nginx worker
# Optional: docker compose up -d llm && docker exec -it hugo-llm-1 ollama pull mistral
```

Nginx: rate limit 10r/s, `client_max_body_size 50M`; optional HTTP Basic and TLS (see `deploy/nginx/`).

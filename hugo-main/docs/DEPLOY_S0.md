# Déploiement S0 — Infra (plan backend Django POC Hugo)

Conforme SPEC §5.1 et §17.1 S0 : 1 VM + docker-compose.

## Services

| Service   | Rôle                          | Image / build      |
|----------|--------------------------------|--------------------|
| postgres | RLS + pgvector                | pgvector/pgvector:pg16 |
| minio    | Stockage S3 (evidence, exports) | minio/minio        |
| redis    | Broker Celery                  | redis:7-alpine     |
| api      | Django (backend)              | build backend/     |
| worker   | Celery (indexation, learner_state) | build backend/ |
| nginx    | TLS, HTTP Basic gate, rate limit, upload 50M | nginx:alpine |
| llm      | Ollama (Mistral 7B CPU)       | ollama/ollama      |

## Démarrage

```bash
# À la racine du repo
cp .env.example .env
# Éditer .env : POSTGRES_PASSWORD, SECRET_KEY obligatoires

# Démarrer la base, le stockage et le broker
docker compose up -d postgres redis minio

# Migrations et superuser
docker compose run --rm api python manage.py migrate --noinput
docker compose run --rm api python manage.py createsuperuser

# Frontend (optionnel) : build pour servir l’interface Vue
cd frontend && npm run build && cd ..

# Démarrer API, nginx, worker (nginx attend que Django réponde)
docker compose up -d api nginx worker
```

**Accès :**
- **Interface (Vue)** : http://localhost:8080/ (login puis tableau de bord)
- **Admin Django** : http://localhost:8080/admin/ ou http://localhost:8000/admin/
- **API directe** : http://localhost:8000/ (sans frontend)
- Si `HTTP_PORT=80` dans `.env` : remplacer 8080 par 80

```bash
# Optionnel : LLM (puis dans le container : ollama pull mistral)
docker compose up -d llm
```

## Nginx

- Fichiers : `deploy/nginx/nginx.conf`, `deploy/nginx/conf.d/api.conf`
- Rate limit : 10 req/s par IP (zone `api_limit`), burst 20
- `client_max_body_size` 50M
- HTTP Basic (gate) : décommenter `auth_basic` et `auth_basic_user_file` dans `api.conf`, créer le fichier avec `htpasswd`
- TLS : décommenter le bloc `server { listen 443 ssl; ... }` et monter les certificats

## Variables (.env)

Voir `.env.example`. En production : définir `SECRET_KEY`, `POSTGRES_PASSWORD`, `DEBUG=0`, `ALLOWED_HOSTS` explicite. Pour le mode production Django : `DJANGO_SETTINGS_MODULE=config.settings.production` et `CORS_ALLOWED_ORIGINS` = URL(s) du frontend (séparées par des virgules).

## MinIO

Le bucket défini par `MINIO_BUCKET` (défaut `hugo-poc`) est créé automatiquement au démarrage de l’API (`ensure_minio_bucket`). Les identifiants MinIO pour l’API sont transmis via `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` (dans compose, dérivés de `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`).

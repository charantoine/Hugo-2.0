# Déploiement sur une VM (POC Hugo)

Checklist pour installer et faire tourner le POC sur une machine (Linux recommandé).

## Prérequis

- Docker et Docker Compose v2
- Git (pour cloner le dépôt ou copier les fichiers)

## 1. Fichiers et configuration

```bash
# Cloner ou copier le projet
cd /opt  # ou répertoire choisi
git clone <repo> hugo-poc && cd hugo-poc

# Copier et éditer l’environnement
cp .env.example .env
```

Éditer `.env` et définir au minimum :

- `POSTGRES_PASSWORD` (fort, non vide)
- `SECRET_KEY` (clé Django, longue et aléatoire)
- `ALLOWED_HOSTS` : hostname(s) et IP de la VM (ex. `hugo.example.com,10.0.0.5`)
- Pour production : `DEBUG=0`, `DJANGO_SETTINGS_MODULE=config.settings.production`, `CORS_ALLOWED_ORIGINS=https://hugo.example.com`
- Optionnel : `HTTP_PORT=80` ou `HTTPS_PORT=443` selon Nginx

## 2. Premier démarrage

```bash
# Démarrer Postgres, Redis, MinIO
docker compose up -d postgres redis minio

# Attendre que Postgres soit healthy, puis migrations
docker compose run --rm api python manage.py migrate --noinput

# Créer un superutilisateur (et l’organisation bootstrap si besoin)
docker compose run --rm api python manage.py createsuperuser

# Build frontend (si pas déjà fait)
cd frontend && npm ci && npm run build && cd ..

# Démarrer tous les services (API crée le bucket MinIO au démarrage)
docker compose up -d api nginx worker
```

Optionnel : `docker compose up -d llm` puis dans le container `ollama pull mistral` pour le chat Hugo.

## 3. Vérifications

- Interface : http://&lt;VM_IP&gt;:8080/ (ou le port configuré)
- Admin : http://&lt;VM_IP&gt;:8080/admin/
- API : http://&lt;VM_IP&gt;:8080/api/ (derrière Nginx)

```bash
docker compose ps
docker compose logs api --tail 50
```

## 4. Sauvegardes (recommandé)

- **Postgres** : dump régulier de la base (RLS et données métier).
  ```bash
  docker compose exec postgres pg_dump -U hugo hugo_poc > backup_$(date +%Y%m%d).sql
  ```
- **MinIO** : sauvegarder le volume `minio_data` (preuves, exports) ou utiliser `mc` pour un miroir.
- **Fichiers** : `.env`, `frontend/dist/` (ou sources + rebuild), `deploy/nginx/`.

## 5. Surveillance (POC minimal)

- Logs : `docker compose logs -f api worker nginx`
- Santé API : le healthcheck Docker utilise le port 8000 (TCP). Pour un check HTTP, utiliser par ex. `GET /api/auth/me/` avec un token valide.
- Redémarrage automatique : les services sont en `restart: unless-stopped` dans le compose.

## 6. TLS (production)

- Obtenir des certificats (Let’s Encrypt, etc.) et les monter dans le container Nginx.
- Dans `deploy/nginx/conf.d/api.conf`, décommenter le bloc `listen 443 ssl` et configurer `ssl_certificate` / `ssl_certificate_key`.
- Optionnel : HTTP Basic en amont (auth_basic + htpasswd) comme indiqué dans `DEPLOY_S0.md`.

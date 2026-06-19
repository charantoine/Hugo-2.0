"""
Django base settings — POC Hugo multi-tenant.
SPEC_POC_v1.5 / .cursorrules: Django + DRF, Postgres RLS, JWT, MinIO.
"""
import os
from pathlib import Path
from typing import Optional, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _env(key: str, default: Optional[str] = None, cast=None):
    val = os.environ.get(key, default)
    if cast is not None and val is not None:
        if cast is bool:
            return val in ("1", "true", "True", "yes")
        return cast(val)
    return val


def _env_list(key: str, default: Optional[List[str]] = None):
    val = os.environ.get(key)
    if val is None:
        return default or []
    return [x.strip() for x in val.split(",") if x.strip()]


def _env_db(key: str, default: str = "postgres://localhost:5432/hugo_poc"):
    val = os.environ.get(key, default)
    if val and val.startswith("postgres://"):
        # Django 4+ prefers postgresql://
        if val.startswith("postgres://"):
            val = "postgresql" + val[8:]
    try:
        from urllib.parse import urlparse
        p = urlparse(val)
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": (p.path or "/").lstrip("/") or "hugo_poc",
            "USER": p.username or "",
            "PASSWORD": p.password or "",
            "HOST": p.hostname or "localhost",
            "PORT": str(p.port or "5432"),
        }
    except Exception:
        return {"ENGINE": "django.db.backends.postgresql", "NAME": "hugo_poc", "USER": "", "PASSWORD": "", "HOST": "localhost", "PORT": "5432"}


SECRET_KEY = _env("SECRET_KEY", "change-me-in-production")
DEBUG = _env("DEBUG", "False", cast=bool)
ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS") or ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    # Local
    "app_core",
    "app_db",
    "apps.accounts",
    "apps.hugo",
    "apps.library",
    "apps.referentials",
    "apps.quality",
    "apps.exports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "app_core.middleware.TenantRLSMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {"default": _env_db("DATABASE_URL")}

AUTH_USER_MODEL = "accounts.User"

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# SimpleJWT: access + refresh, rotation/blacklist
from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# CORS (dev; override in dev.py / production.py)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = []

# S3/MinIO
AWS_ACCESS_KEY_ID = _env("MINIO_ACCESS_KEY", "minioadmin")
AWS_SECRET_ACCESS_KEY = _env("MINIO_SECRET_KEY", "minioadmin")
AWS_STORAGE_BUCKET_NAME = _env("MINIO_BUCKET", "hugo-poc")
AWS_S3_ENDPOINT_URL = _env("MINIO_ENDPOINT", "http://localhost:9000")
AWS_S3_REGION_NAME = _env("MINIO_REGION", "us-east-1")
AWS_S3_USE_SSL = _env("MINIO_USE_SSL", "false", cast=bool)
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = True
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# Celery
CELERY_BROKER_URL = _env("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = _env("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# LLM (Mistral local / provider générique)
LLM_BASE_URL = _env("LLM_BASE_URL", "http://localhost:11434")
LLM_MODEL = _env("LLM_MODEL", "mistral")
LLM_PROVIDER_DEFAULT = _env("LLM_PROVIDER_DEFAULT", "ollama")  # "ollama" ou "ovh_ai"
ENABLE_EXTERNAL_LLM = _env("ENABLE_EXTERNAL_LLM", "true", cast=bool)
HUGO_DEBUG_TRACING = _env("HUGO_DEBUG_TRACING", "true" if DEBUG else "false", cast=bool)

# Hugo phase classifier runtime tuning
HUGO_PHASE_CLASSIFIER_ENABLED = _env("HUGO_PHASE_CLASSIFIER_ENABLED", "true", cast=bool)
HUGO_PHASE_CLASSIFIER_MAX_TOKENS = _env("HUGO_PHASE_CLASSIFIER_MAX_TOKENS", "48", cast=int)
HUGO_PHASE_CLASSIFIER_MIN_CONFIDENCE = _env("HUGO_PHASE_CLASSIFIER_MIN_CONFIDENCE", "0.60", cast=float)
HUGO_PHASE_CLASSIFIER_MAX_INPUT_CHARS = _env("HUGO_PHASE_CLASSIFIER_MAX_INPUT_CHARS", "700", cast=int)
HUGO_P0_CLASSIFIER_ENABLED = _env("HUGO_P0_CLASSIFIER_ENABLED", "false", cast=bool)
HUGO_P0_CLASSIFIER_MAX_TOKENS = _env("HUGO_P0_CLASSIFIER_MAX_TOKENS", "180", cast=int)
HUGO_P0_CLASSIFIER_MIN_CONFIDENCE = _env("HUGO_P0_CLASSIFIER_MIN_CONFIDENCE", "0.60", cast=float)
HUGO_P0_CLASSIFIER_MAX_INPUT_CHARS = _env("HUGO_P0_CLASSIFIER_MAX_INPUT_CHARS", "900", cast=int)
HUGO_P0_V17_ENABLED = _env("HUGO_P0_V17_ENABLED", "false", cast=bool)

# OVH AI Endpoints (POST-POC / optionnel)
OVH_AI_BASE_URL = _env("OVH_AI_BASE_URL", "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1")
OVH_AI_MODEL = _env("OVH_AI_MODEL", "Llama-3.1-8B-Instruct")
OVH_AI_TOKEN = _env("OVH_AI_TOKEN", "eyJhbGciOiJFZERTQSIsImtpZCI6IjgzMkFGNUE5ODg3MzFCMDNGM0EzMTRFMDJFRUJFRjBGNDE5MUY0Q0YiLCJraW5kIjoicGF0IiwidHlwIjoiSldUIn0.eyJ0b2tlbiI6IjRHZ1BpWFFqeVYrNUtGSzBIZ1RoZFhJOE9nQjhJa1VlYjBXMWJvNFJjNWc9In0.WbZh1sYV7ykCMpZHhTCJ-3I8RCXECBN4x-49r5s-Qu-3rFjTVo-bVnmvm9Y0zJnQ2_lQNjNLKbBLotRscPQECg")
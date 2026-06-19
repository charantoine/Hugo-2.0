"""Production settings — POC Hugo (DEBUG=0, CORS restreint)."""
import os
from .base import *  # noqa: F401, F403

DEBUG = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    x.strip()
    for x in (os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:8080").split(","))
    if x.strip()
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# URL publique des fichiers statiques
STATIC_URL = "/static/"

# Dossier sur le disque où collectstatic va tout rassembler
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # adapte si besoin

STATIC_ROOT = BASE_DIR / "static"
# ou, si tu préfères, BASE_DIR / "staticfiles"
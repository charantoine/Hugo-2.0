"""SQLite test settings for local CI-style verification."""
from .base import *  # noqa: F401, F403

DEBUG = False
SECRET_KEY = "sqlite-test-secret-key"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test.sqlite3",
    }
}
MIGRATION_MODULES = {
    "accounts": None,
    "hugo": None,
    "library": None,
    "referentials": None,
    "quality": None,
    "exports": None,
    "app_db": None,
}
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
AWS_STORAGE_BUCKET_NAME = "test-bucket"

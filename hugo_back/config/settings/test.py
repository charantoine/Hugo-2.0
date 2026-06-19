"""Test settings — POC Hugo (pytest-django)."""
import os
from .base import *  # noqa: F401, F403

DEBUG = False
SECRET_KEY = "test-secret-key"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("TEST_DB_NAME", "hugo_poc_test"),
        "USER": os.environ.get("TEST_DB_USER", "postgres"),
        "PASSWORD": os.environ.get("TEST_DB_PASSWORD", ""),
        "HOST": os.environ.get("TEST_DB_HOST", "localhost"),
        "PORT": os.environ.get("TEST_DB_PORT", "5432"),
    }
}
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
# MinIO: use in-memory or fake in tests if needed
AWS_STORAGE_BUCKET_NAME = "test-bucket"

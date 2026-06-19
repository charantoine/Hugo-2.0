"""Development settings — POC Hugo."""
from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True  # Nginx handles in prod

# Logging: no verbatim content (metadata only)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "metadata": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "metadata",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

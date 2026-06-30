from django.apps import AppConfig
import logging


class AppCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_core"
    label = "app_core"
    verbose_name = "Core (security, logging, tenant)"

    def ready(self):
        # Log once at startup (runserver, gunicorn, tests) — helps distinguish hugo_poc vs sqlite_test.
        try:
            from app_core.runtime_stack import format_runtime_stack_line

            logging.getLogger("hugo.runtime").info(format_runtime_stack_line())
        except Exception:
            pass

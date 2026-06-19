from django.apps import AppConfig


class AppCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_core"
    label = "app_core"
    verbose_name = "Core (security, logging, tenant)"

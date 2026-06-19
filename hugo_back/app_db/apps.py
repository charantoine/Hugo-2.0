from django.apps import AppConfig


class AppDbConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_db"
    label = "app_db"
    verbose_name = "DB (RLS helpers, Postgres)"

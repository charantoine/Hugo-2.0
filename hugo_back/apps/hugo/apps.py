from django.apps import AppConfig


class HugoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.hugo"
    label = "hugo"
    verbose_name = "Hugo (chat, traces, partage)"

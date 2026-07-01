"""Applique les patches schéma persona sur SQLite locale (baseline B)."""
from django.core.management.base import BaseCommand

from apps.hugo.services.sqlite_schema_patches import ensure_persona_schema


class Command(BaseCommand):
    help = "Ensure persona schema (0022) exists on local SQLite when migrations are disabled."

    def handle(self, *args, **options):
        changes = ensure_persona_schema()
        if not changes:
            self.stdout.write(self.style.SUCCESS("Persona schema already up to date."))
            return
        for item in changes:
            self.stdout.write(self.style.SUCCESS(f"Applied: {item}"))

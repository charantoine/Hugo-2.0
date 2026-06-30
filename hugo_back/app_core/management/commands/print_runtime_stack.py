"""Print active Django settings module and database (local stack diagnostic)."""
from django.core.management.base import BaseCommand

from app_core.runtime_stack import describe_runtime_stack, format_runtime_stack_line


class Command(BaseCommand):
    help = "Affiche la stack locale active (settings + base de données)."

    def handle(self, *args, **options):
        info = describe_runtime_stack()
        self.stdout.write(format_runtime_stack_line())
        for key, value in info.items():
            self.stdout.write(f"  {key}: {value}")

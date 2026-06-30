"""Tests for runtime stack descriptor."""
from django.test import SimpleTestCase, override_settings

from app_core.runtime_stack import describe_runtime_stack, format_runtime_stack_line


class RuntimeStackTests(SimpleTestCase):
    @override_settings(DATABASES={"default": {"ENGINE": "django.db.backends.postgresql", "NAME": "hugo_poc"}})
    def test_describe_postgres_dev_stack(self):
        info = describe_runtime_stack()
        self.assertEqual(info["stack_kind"], "postgres_dev")
        self.assertEqual(info["db_name"], "hugo_poc")

    @override_settings(DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "/tmp/test.sqlite3"}})
    def test_describe_sqlite_stack(self):
        info = describe_runtime_stack()
        self.assertEqual(info["stack_kind"], "sqlite_smoke")

    def test_format_line_non_empty(self):
        line = format_runtime_stack_line()
        self.assertIn("Hugo runtime stack", line)

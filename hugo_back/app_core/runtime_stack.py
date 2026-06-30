"""Runtime stack descriptor — which settings module and database are active."""
from __future__ import annotations

import os

from django.conf import settings


def describe_runtime_stack() -> dict[str, str]:
    db = settings.DATABASES.get("default", {})
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "unknown")
    engine = str(db.get("ENGINE", ""))
    name = str(db.get("NAME", ""))
    if "sqlite" in engine:
        stack_kind = "sqlite_smoke"
    elif "postgresql" in engine:
        stack_kind = "postgres_dev"
    else:
        stack_kind = "other"
    return {
        "settings_module": settings_module,
        "db_engine": engine,
        "db_name": name,
        "stack_kind": stack_kind,
    }


def format_runtime_stack_line() -> str:
    info = describe_runtime_stack()
    return (
        f"Hugo runtime stack: settings={info['settings_module']} "
        f"db={info['db_name']} ({info['stack_kind']})"
    )

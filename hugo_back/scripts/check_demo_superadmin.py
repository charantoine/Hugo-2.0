#!/usr/bin/env python3
"""Read-only inspection of demo.superadmin on the active Django database."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django

django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model


def main() -> int:
    db = settings.DATABASES["default"]
    print("DJANGO_SETTINGS_MODULE:", os.environ.get("DJANGO_SETTINGS_MODULE"))
    print("Database engine:", db.get("ENGINE"))
    print("Database name:", db.get("NAME"))
    print("Database host:", db.get("HOST") or "(default)")

    User = get_user_model()
    qs = User.objects.filter(username="demo.superadmin").select_related("organisation")
    count = qs.count()
    print("\ndemo.superadmin count:", count)
    if count == 0:
        print("NOT FOUND — do not reset password.")
        return 1
    if count > 1:
        print("DUPLICATE USERNAMES — abort.")
        return 2

    user = qs.first()
    print("id:", user.id)
    print("username:", user.username)
    print("role:", user.role)
    print("is_superuser:", user.is_superuser)
    print("is_staff:", user.is_staff)
    print("is_active:", user.is_active)
    print("organisation:", user.organisation.name if user.organisation_id else None)
    print("organisation_id:", user.organisation_id)
    print("email:", user.email or "(empty)")
    print("last_login:", user.last_login)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

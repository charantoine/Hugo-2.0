"""RLS environment checks — prod-like CI must not use a role that bypasses RLS."""
from __future__ import annotations

import os

from django.db import connection


def connection_bypasses_rls() -> bool:
    """True when current DB role is superuser, BYPASSRLS, or unforced table owner."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT rolsuper OR rolbypassrls FROM pg_roles WHERE rolname = current_user"
        )
        row = cursor.fetchone()
        if row and row[0]:
            return True
        cursor.execute(
            """
            SELECT bool_or(c.relowner = (SELECT oid FROM pg_roles WHERE rolname = current_user)
                           AND NOT c.relforcerowsecurity)
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'hugo_session' AND n.nspname = 'public'
            """
        )
        row = cursor.fetchone()
        return bool(row and row[0])


def rls_strict_mode_enabled() -> bool:
    """When true, tests fail instead of skip if RLS cannot be verified."""
    return os.environ.get("HUGO_RLS_STRICT", "").lower() in {"1", "true", "yes"}


def assert_rls_environment_usable_for_audit():
    """
    In strict mode (CI prod-like), fail if the migration connection bypasses RLS.
    Application runtime should use a dedicated non-superuser role (see setup_rls_app_role.sql).
    """
    if not rls_strict_mode_enabled():
        return
    if connection_bypasses_rls():
        raise AssertionError(
            "HUGO_RLS_STRICT=1 but current DB role bypasses RLS (superuser/owner). "
            "Use role hugo_app / hugo_app_tenant_test — see scripts/setup_rls_app_role.sql"
        )

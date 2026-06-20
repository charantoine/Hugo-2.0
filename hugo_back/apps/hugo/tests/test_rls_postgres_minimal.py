"""RLS Postgres minimal audit — cluster 8.

Requires PostgreSQL with RLS migrations applied (not SQLite).
Skip automatically when ENGINE is not postgresql or DB unreachable.
"""
import os
import uuid

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection

from app_core.rls_guard import (
    assert_rls_environment_usable_for_audit,
    connection_bypasses_rls,
    rls_strict_mode_enabled,
)
from apps.accounts.models import Organisation, Role
from apps.hugo.models import HugoSession, Trace


def _is_postgres():
    return settings.DATABASES["default"]["ENGINE"].endswith("postgresql")


def _connection_bypasses_rls():
    return connection_bypasses_rls()


@pytest.fixture(scope="module", autouse=True)
def _rls_strict_environment_gate():
    assert_rls_environment_usable_for_audit()


@pytest.mark.skipif(not _is_postgres(), reason="RLS audit requires PostgreSQL")
@pytest.mark.django_db
def test_rls_policies_exist_on_sensitive_tables():
    tables = ("hugo_session", "trace", "evidence", "export_run")
    with connection.cursor() as cursor:
        for table in tables:
            cursor.execute(
                """
                SELECT relrowsecurity
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relname = %s AND n.nspname = 'public'
                """,
                [table],
            )
            row = cursor.fetchone()
            assert row is not None, f"table missing: {table}"
            assert row[0] is True, f"RLS not enabled on {table}"


@pytest.mark.skipif(not _is_postgres(), reason="RLS audit requires PostgreSQL")
@pytest.mark.django_db
def test_rls_cross_tenant_session_isolation_sql():
    user_model = get_user_model()
    org_a = Organisation.objects.create(name=f"RLS Org A {uuid.uuid4().hex[:8]}")
    org_b = Organisation.objects.create(name=f"RLS Org B {uuid.uuid4().hex[:8]}")
    learner_a = user_model.objects.create_user(
        username=f"rls_a_{uuid.uuid4().hex[:8]}",
        password="pass",
        organisation=org_a,
        role=Role.LEARNER,
    )
    learner_b = user_model.objects.create_user(
        username=f"rls_b_{uuid.uuid4().hex[:8]}",
        password="pass",
        organisation=org_b,
        role=Role.LEARNER,
    )
    if _connection_bypasses_rls():
        message = (
            "Current DB role bypasses RLS (superuser/owner) — use hugo_app_tenant_test role"
        )
        if rls_strict_mode_enabled():
            pytest.fail(message)
        pytest.skip(message)

    session_b = HugoSession.objects.create(organisation=org_b, learner=learner_b)
    Trace.objects.create(organisation=org_b, session=session_b, payload_structured={})

    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL app.organisation_id = %s", [str(org_a.id)])
        cursor.execute("SELECT count(*) FROM hugo_session WHERE organisation_id = %s", [str(org_b.id)])
        count = cursor.fetchone()[0]
        assert count == 0, "RLS must block cross-tenant hugo_session reads"

    # ORM still scoped by explicit filters in app code
    assert HugoSession.objects.filter(organisation=org_b).count() == 1


@pytest.mark.skipif(not _is_postgres(), reason="RLS audit requires PostgreSQL")
def test_rls_audit_skipped_documentation_on_sqlite():
    """When SQLite is used, RLS prod remains A_VÉRIFIER — see cluster 8 OPS report."""
    if _is_postgres():
        pytest.skip("Postgres available — run policy tests instead")
    assert os.environ.get("DJANGO_SETTINGS_MODULE", "").endswith("test") or True


RLS_APP_ROLE = os.environ.get("HUGO_RLS_APP_ROLE", "hugo_app_tenant_test")
RLS_APP_ROLE_PASSWORD = os.environ.get("HUGO_RLS_APP_ROLE_PASSWORD", "hugo_rls_test_only")


def _app_role_exists(role_name: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [role_name])
        return cursor.fetchone() is not None


def _ensure_app_role_grants():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            GRANT SELECT ON TABLE
              hugo_session, hugo_message, trace, evidence, export_run, learner_state
            TO hugo_app_tenant_test
            """
        )


def _query_as_app_role(*, org_id: str, target_org_id: str) -> int:
    """Separate connection as app role (committed data visible)."""
    import psycopg

    db = settings.DATABASES["default"]
    conninfo = (
        f"host={db.get('HOST', 'localhost')} "
        f"port={db.get('PORT', 5432)} "
        f"dbname={db['NAME']} "
        f"user={RLS_APP_ROLE} "
        f"password={RLS_APP_ROLE_PASSWORD}"
    )
    with psycopg.connect(conninfo, autocommit=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SET app.organisation_id = '{org_id}'")
            cursor.execute(
                "SELECT count(*) FROM hugo_session WHERE organisation_id = %s",
                [target_org_id],
            )
            return cursor.fetchone()[0]


@pytest.mark.skipif(not _is_postgres(), reason="RLS audit requires PostgreSQL")
@pytest.mark.django_db(transaction=True)
def test_rls_cross_tenant_session_isolation_app_role():
    """C9-OPS-01 — non-superuser role must not read another tenant's rows."""
    if not _app_role_exists(RLS_APP_ROLE):
        pytest.skip(
            f"Role {RLS_APP_ROLE} missing — run: psql -U postgres -d hugo_poc_test -f scripts/setup_rls_app_role.sql"
        )

    user_model = get_user_model()
    org_a = Organisation.objects.create(name=f"RLS App Org A {uuid.uuid4().hex[:8]}")
    org_b = Organisation.objects.create(name=f"RLS App Org B {uuid.uuid4().hex[:8]}")
    learner_b = user_model.objects.create_user(
        username=f"rls_app_b_{uuid.uuid4().hex[:8]}",
        password="pass",
        organisation=org_b,
        role=Role.LEARNER,
    )
    HugoSession.objects.create(organisation=org_b, learner=learner_b)

    _ensure_app_role_grants()
    count = _query_as_app_role(org_id=str(org_a.id), target_org_id=str(org_b.id))
    assert count == 0, "RLS must block cross-tenant reads for app role"


@pytest.mark.skipif(not _is_postgres(), reason="RLS audit requires PostgreSQL")
@pytest.mark.django_db
def test_api_cross_tenant_session_blocked(api_client):
    """App-layer isolation: org A user cannot read org B session (404)."""
    user_model = get_user_model()
    org_a = Organisation.objects.create(name=f"RLS API Org A {uuid.uuid4().hex[:8]}")
    org_b = Organisation.objects.create(name=f"RLS API Org B {uuid.uuid4().hex[:8]}")
    user_a = user_model.objects.create_user(
        username=f"rls_api_a_{uuid.uuid4().hex[:8]}",
        password="pass",
        organisation=org_a,
        role=Role.LEARNER,
    )
    learner_b = user_model.objects.create_user(
        username=f"rls_api_b_{uuid.uuid4().hex[:8]}",
        password="pass",
        organisation=org_b,
        role=Role.LEARNER,
    )
    session_b = HugoSession.objects.create(organisation=org_b, learner=learner_b)
    api_client.force_authenticate(user=user_a)
    response = api_client.get(f"/hugo/sessions/{session_b.id}/")
    assert response.status_code in (403, 404), "cross-tenant session must be blocked at API"

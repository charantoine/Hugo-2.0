"""
RLS helpers — run RLS policies with current_setting('app.organisation_id', true).
All business tables use: organisation_id = current_setting('app.organisation_id', true)::uuid
"""
from django.db import connection


def get_current_organisation_id():
    """Return current app.organisation_id from session (for tests/debug)."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_setting('app.organisation_id', true)")
        row = cursor.fetchone()
    if row and row[0]:
        return row[0]
    return None


def enable_rls_sql(table_name: str, policy_name=None):
    """
    Return SQL statements to enable RLS and create tenant isolation policy.
    policy_name defaults to {table_name}_tenant_isolation.
    """
    name = policy_name or f"{table_name}_tenant_isolation"
    return [
        "ALTER TABLE %s ENABLE ROW LEVEL SECURITY;" % table_name,
        ("CREATE POLICY %s ON %s "
         "USING (organisation_id = current_setting('app.organisation_id', true)::uuid) "
         "WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);") % (name, table_name),
    ]

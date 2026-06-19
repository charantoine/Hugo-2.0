# RLS on hugo_session, hugo_message, trace, evidence, learner_state
from django.db import migrations

TABLES = [
    "hugo_session",
    "hugo_message",
    "trace",
    "evidence",
    "learner_state",
]


def _ops():
    ops = []
    for table in TABLES:
        name = table + "_tenant_isolation"
        ops.append(
            migrations.RunSQL(
                "ALTER TABLE %s ENABLE ROW LEVEL SECURITY;" % table,
                reverse_sql="ALTER TABLE %s DISABLE ROW LEVEL SECURITY;" % table,
            )
        )
        ops.append(
            migrations.RunSQL(
                """CREATE POLICY %s ON %s
  USING (organisation_id = current_setting('app.organisation_id', true)::uuid)
  WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);""" % (name, table),
                reverse_sql="DROP POLICY IF EXISTS %s ON %s;" % (name, table),
            )
        )
    return ops


class Migration(migrations.Migration):

    dependencies = [
        ("hugo", "0001_initial"),
    ]

    operations = _ops()

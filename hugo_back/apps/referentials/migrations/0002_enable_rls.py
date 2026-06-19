# RLS on group, group_membership, tutor_learner_link
from django.db import migrations


def _policy(table, name=None):
    n = name or (table + "_tenant_isolation")
    quoted = '"' + table + '"'
    return [
        migrations.RunSQL(
            "ALTER TABLE %s ENABLE ROW LEVEL SECURITY;" % quoted,
            reverse_sql="ALTER TABLE %s DISABLE ROW LEVEL SECURITY;" % quoted,
        ),
        migrations.RunSQL(
            """CREATE POLICY %s ON %s
  USING (organisation_id = current_setting('app.organisation_id', true)::uuid)
  WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);""" % (n, quoted),
            reverse_sql="DROP POLICY IF EXISTS %s ON %s;" % (n, quoted),
        ),
    ]


class Migration(migrations.Migration):

    dependencies = [
        ("referentials", "0001_groups_initial"),
    ]

    operations = _policy("group") + _policy("group_membership") + _policy("tutor_learner_link")

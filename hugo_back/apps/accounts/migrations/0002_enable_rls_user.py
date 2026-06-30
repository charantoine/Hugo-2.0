# RLS on user table: tenant isolation by organisation_id
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE " + '"user"' + " ENABLE ROW LEVEL SECURITY;",
            reverse_sql="ALTER TABLE " + '"user"' + " DISABLE ROW LEVEL SECURITY;",
        ),
        migrations.RunSQL(
            """CREATE POLICY user_tenant_isolation ON "user"
  USING (organisation_id = current_setting('app.organisation_id', true)::uuid)
  WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);""",
            reverse_sql='DROP POLICY IF EXISTS user_tenant_isolation ON "user";',
        ),
    ]

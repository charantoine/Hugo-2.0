from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [("quality", "0001_initial")]
    operations = [
        migrations.RunSQL(
            "ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;",
            reverse_sql="ALTER TABLE audit_log DISABLE ROW LEVEL SECURITY;",
        ),
        migrations.RunSQL(
            "CREATE POLICY audit_log_tenant_isolation ON audit_log USING (organisation_id = current_setting('app.organisation_id', true)::uuid) WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);",
            reverse_sql="DROP POLICY IF EXISTS audit_log_tenant_isolation ON audit_log;",
        ),
    ]

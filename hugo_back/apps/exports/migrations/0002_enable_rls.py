from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [("exports", "0001_initial")]
    operations = [
        migrations.RunSQL(
            "ALTER TABLE export_run ENABLE ROW LEVEL SECURITY;",
            reverse_sql="ALTER TABLE export_run DISABLE ROW LEVEL SECURITY;",
        ),
        migrations.RunSQL(
            "CREATE POLICY export_run_tenant_isolation ON export_run USING (organisation_id = current_setting('app.organisation_id', true)::uuid) WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);",
            reverse_sql="DROP POLICY IF EXISTS export_run_tenant_isolation ON export_run;",
        ),
    ]

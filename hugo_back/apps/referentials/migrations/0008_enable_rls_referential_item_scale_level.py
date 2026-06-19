# RLS on scale_level and referential_item (now have organisation_id).
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("referentials", "0007_enforce_org_not_null")]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE scale_level ENABLE ROW LEVEL SECURITY;",
            reverse_sql="ALTER TABLE scale_level DISABLE ROW LEVEL SECURITY;",
        ),
        migrations.RunSQL(
            "CREATE POLICY scale_level_tenant_isolation ON scale_level USING (organisation_id = current_setting('app.organisation_id', true)::uuid) WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);",
            reverse_sql="DROP POLICY IF EXISTS scale_level_tenant_isolation ON scale_level;",
        ),
        migrations.RunSQL(
            "ALTER TABLE referential_item ENABLE ROW LEVEL SECURITY;",
            reverse_sql="ALTER TABLE referential_item DISABLE ROW LEVEL SECURITY;",
        ),
        migrations.RunSQL(
            "CREATE POLICY referential_item_tenant_isolation ON referential_item USING (organisation_id = current_setting('app.organisation_id', true)::uuid) WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);",
            reverse_sql="DROP POLICY IF EXISTS referential_item_tenant_isolation ON referential_item;",
        ),
    ]


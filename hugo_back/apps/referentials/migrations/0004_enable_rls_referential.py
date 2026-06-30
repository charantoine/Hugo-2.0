# RLS on scale, referential, referential_config, referential_item_overlay (have organisation_id)
from django.db import migrations

TABLES = ["scale", "referential", "referential_config", "referential_item_overlay"]


def ops():
    o = []
    for t in TABLES:
        n = t + "_tenant_isolation"
        o.append(migrations.RunSQL(
            "ALTER TABLE %s ENABLE ROW LEVEL SECURITY;" % t,
            reverse_sql="ALTER TABLE %s DISABLE ROW LEVEL SECURITY;" % t,
        ))
        o.append(migrations.RunSQL(
            "CREATE POLICY %s ON %s USING (organisation_id = current_setting('app.organisation_id', true)::uuid) WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);" % (n, t),
            reverse_sql="DROP POLICY IF EXISTS %s ON %s;" % (n, t),
        ))
    return o


class Migration(migrations.Migration):
    dependencies = [("referentials", "0003_referential_scale_overlay")]
    operations = ops()

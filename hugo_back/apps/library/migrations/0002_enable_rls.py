# RLS on document, group_document, rag_citation (document_chunk accessed via document)
from django.db import migrations

TABLES = ["document", "group_document", "rag_citation"]


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
    dependencies = [("library", "0001_initial")]
    operations = ops()

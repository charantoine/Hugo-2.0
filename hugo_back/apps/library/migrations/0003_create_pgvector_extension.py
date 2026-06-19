from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("library", "0002_enable_rls"),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS vector;",
            reverse_sql="DROP EXTENSION IF EXISTS vector;",
        ),
    ]


# Enforce organisation_id NOT NULL after backfill.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("referentials", "0006_backfill_org_fields")]

    operations = [
        migrations.AlterField(
            model_name="referentialitem",
            name="organisation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="referential_items",
                to="accounts.organisation",
                null=False,
                blank=False,
            ),
        ),
        migrations.AlterField(
            model_name="scalelevel",
            name="organisation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="scale_levels",
                to="accounts.organisation",
                null=False,
                blank=False,
            ),
        ),
    ]


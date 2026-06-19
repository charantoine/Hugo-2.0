# Backfill organisation_id for scale_level and referential_item from their parent FK.
from django.db import migrations


def forwards(apps, schema_editor):
    ScaleLevel = apps.get_model("referentials", "ScaleLevel")
    ReferentialItem = apps.get_model("referentials", "ReferentialItem")

    for sl in ScaleLevel.objects.select_related("scale", "scale__organisation").all():
        if sl.organisation_id is None and sl.scale_id is not None:
            sl.organisation_id = sl.scale.organisation_id
            sl.save(update_fields=["organisation"])

    for item in ReferentialItem.objects.select_related("referential", "referential__organisation").all():
        if item.organisation_id is None and item.referential_id is not None:
            item.organisation_id = item.referential.organisation_id
            item.save(update_fields=["organisation"])


def backwards(apps, schema_editor):
    ScaleLevel = apps.get_model("referentials", "ScaleLevel")
    ReferentialItem = apps.get_model("referentials", "ReferentialItem")
    ScaleLevel.objects.update(organisation=None)
    ReferentialItem.objects.update(organisation=None)


class Migration(migrations.Migration):
    dependencies = [("referentials", "0005_add_org_fields")]
    operations = [migrations.RunPython(forwards, backwards)]


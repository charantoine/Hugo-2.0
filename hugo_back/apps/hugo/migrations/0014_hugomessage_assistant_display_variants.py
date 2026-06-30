from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hugo", "0013_hugosession_p0_classifier_enabled_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="hugomessage",
            name="assistant_display_variants",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]

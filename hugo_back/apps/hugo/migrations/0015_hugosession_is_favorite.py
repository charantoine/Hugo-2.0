from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hugo", "0014_hugomessage_assistant_display_variants"),
    ]

    operations = [
        migrations.AddField(
            model_name="hugosession",
            name="is_favorite",
            field=models.BooleanField(
                default=False,
                help_text="Learner-marked favorite for quick retrieval in the UI.",
            ),
        ),
    ]

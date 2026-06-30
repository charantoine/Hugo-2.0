from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hugo", "0020_learner_conversation_global_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="trainerknowledgeitem",
            name="meta",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]

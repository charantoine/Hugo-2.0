from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("referentials", "0016_group_p0_classifier_enabled_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="group",
            name="learner_display_profile",
            field=models.CharField(
                choices=[
                    ("youth", "Youth"),
                    ("adult", "Adult"),
                    ("professional", "Professional"),
                ],
                default="professional",
                max_length=32,
            ),
        ),
    ]

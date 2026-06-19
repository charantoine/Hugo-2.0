from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_relax_rls_user_bootstrap"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="default_learner_display_profile",
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

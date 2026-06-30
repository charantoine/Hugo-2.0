import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hugo", "0020_learner_conversation_global_profile"),
        ("referentials", "0017_group_learner_display_profile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="default_tutor_prompt",
            field=models.ForeignKey(
                blank=True,
                help_text="Legacy: single TutorPrompt default. Prefer default_learner_conversation_profile.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="groups_with_default_tutor_prompt",
                to="hugo.tutorprompt",
            ),
        ),
        migrations.AddField(
            model_name="group",
            name="default_learner_conversation_profile",
            field=models.ForeignKey(
                blank=True,
                help_text="Global learner conversation profile for this group.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="groups_with_default_profile",
                to="hugo.learnerconversationglobalprofile",
            ),
        ),
    ]

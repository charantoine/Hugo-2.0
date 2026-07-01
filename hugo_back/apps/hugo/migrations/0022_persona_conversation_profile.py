import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("hugo", "0021_trainer_knowledge_item_meta"),
    ]

    operations = [
        migrations.AddField(
            model_name="tutorprompt",
            name="persona_scope",
            field=models.CharField(
                choices=[
                    ("learner", "Learner"),
                    ("tutor", "Tutor"),
                    ("trainer", "Trainer"),
                ],
                default="learner",
                help_text="Scope métier du prompt (apprenant vs persona tuteur/formateur).",
                max_length=16,
            ),
        ),
        migrations.CreateModel(
            name="PersonaConversationProfile",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "persona",
                    models.CharField(
                        choices=[("tutor", "Tutor"), ("trainer", "Trainer")],
                        max_length=16,
                    ),
                ),
                ("code", models.SlugField(max_length=100)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("active", "Active"),
                            ("inactive", "Inactive"),
                        ],
                        default="active",
                        max_length=16,
                    ),
                ),
                (
                    "is_default",
                    models.BooleanField(
                        default=False,
                        help_text="Default persona profile for this organisation and persona kind.",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="persona_conversation_profiles",
                        to="accounts.organisation",
                    ),
                ),
                (
                    "tutor_prompt",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="persona_profiles",
                        to="hugo.tutorprompt",
                    ),
                ),
            ],
            options={
                "db_table": "persona_conversation_profile",
                "ordering": ["organisation_id", "persona", "name"],
                "unique_together": {("organisation", "persona", "code")},
            },
        ),
        migrations.AddField(
            model_name="hugosession",
            name="persona_conversation_profile",
            field=models.ForeignKey(
                blank=True,
                help_text="Optional persona profile (tuteur/formateur) for this session.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sessions",
                to="hugo.personaconversationprofile",
            ),
        ),
    ]

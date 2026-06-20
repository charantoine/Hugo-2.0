import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("hugo", "0019_d9bis_analytics_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="LearnerConversationGlobalProfile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("active", "Active"), ("inactive", "Inactive")],
                        default="active",
                        max_length=16,
                    ),
                ),
                (
                    "is_default",
                    models.BooleanField(
                        default=False,
                        help_text="If true, used as organisation default when no group/session profile is set.",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "diagnostic_conduct_profile",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="global_profiles_diagnostic_conduct",
                        to="hugo.tutorconductprofile",
                    ),
                ),
                (
                    "diagnostic_tutor_prompt",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="global_profiles_diagnostic",
                        to="hugo.tutorprompt",
                    ),
                ),
                (
                    "evaluation_policy",
                    models.ForeignKey(
                        blank=True,
                        help_text="Optional organisation-level evaluation policy linked to this profile.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="global_profiles",
                        to="hugo.evaluationpolicy",
                    ),
                ),
                (
                    "evaluation_prompt_profile",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="global_profiles_evaluation",
                        to="hugo.evaluationpromptprofile",
                    ),
                ),
                (
                    "knowledge_review_conduct_profile",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="global_profiles_knowledge_review_conduct",
                        to="hugo.tutorconductprofile",
                    ),
                ),
                (
                    "knowledge_review_tutor_prompt",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="global_profiles_knowledge_review",
                        to="hugo.tutorprompt",
                    ),
                ),
                (
                    "organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learner_conversation_global_profiles",
                        to="accounts.organisation",
                    ),
                ),
                (
                    "reflective_conduct_profile",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="global_profiles_reflective_conduct",
                        to="hugo.tutorconductprofile",
                    ),
                ),
                (
                    "reflective_tutor_prompt",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="global_profiles_reflective",
                        to="hugo.tutorprompt",
                    ),
                ),
            ],
            options={
                "db_table": "learner_conversation_global_profile",
                "ordering": ["organisation_id", "name"],
                "unique_together": {("organisation", "name")},
            },
        ),
        migrations.AddField(
            model_name="hugosession",
            name="learner_conversation_profile",
            field=models.ForeignKey(
                blank=True,
                help_text="Optional global learner conversation profile for this session.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sessions",
                to="hugo.learnerconversationglobalprofile",
            ),
        ),
    ]

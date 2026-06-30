from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("referentials", "0001_groups_initial"),
        ("hugo", "0017_hugosession_analytics_state_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="hugosession",
            name="evaluation_in_progress",
            field=models.BooleanField(
                default=False,
                help_text="True while an evaluation workflow is being prepared or reviewed.",
            ),
        ),
        migrations.CreateModel(
            name="TutorConductProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("posture", models.CharField(choices=[("diagnostic", "Diagnostic"), ("reflective_afest", "Réflexif AFEST"), ("knowledge_review", "Savoirs / révision")], default="reflective_afest", max_length=64)),
                ("system_template", models.TextField()),
                ("user_template", models.TextField(blank=True, default="")),
                ("max_questions_per_turn", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("forbidden_moves", models.JSONField(blank=True, default=list)),
                ("allowed_moves", models.JSONField(blank=True, default=list)),
                ("closure_policy", models.CharField(blank=True, default="", max_length=64)),
                ("description", models.TextField(blank=True, default="")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organisation", models.ForeignKey(blank=True, help_text="Null = fallback system profile.", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="tutor_conduct_profiles", to="accounts.organisation")),
            ],
            options={
                "db_table": "tutor_conduct_profile",
                "ordering": ["posture", "organisation_id"],
                "unique_together": {("organisation", "posture")},
            },
        ),
        migrations.CreateModel(
            name="EvaluationPromptProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(db_index=True, max_length=64)),
                ("label", models.CharField(max_length=128)),
                ("is_active", models.BooleanField(default=True)),
                ("prompt_frame", models.TextField()),
                ("prompt_judgement_guide", models.TextField()),
                ("prompt_output_guide", models.TextField()),
                ("max_dialogue_turns", models.PositiveSmallIntegerField(default=6)),
                ("ask_learner_confirmation", models.BooleanField(default=True)),
                ("human_validation_required", models.BooleanField(default=True)),
                ("updated_by", models.CharField(blank=True, default="", max_length=128)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("organisation", models.ForeignKey(blank=True, help_text="Null = global fallback profile.", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="evaluation_prompt_profiles", to="accounts.organisation")),
            ],
            options={
                "db_table": "evaluation_prompt_profile",
                "ordering": ["organisation_id", "code"],
                "unique_together": {("organisation", "code")},
            },
        ),
        migrations.CreateModel(
            name="EvaluationPolicy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("share_with_tutor", models.BooleanField(default=True)),
                ("tutor_validation_required", models.BooleanField(default=False)),
                ("allow_early_trigger", models.BooleanField(default=True)),
                ("early_trigger_warning", models.TextField(default="La conversation n'est pas encore suffisamment mûre. L'évaluation sera partielle.")),
                ("trainer_directives", models.TextField(blank=True, default="")),
                ("evaluation_profile_code", models.CharField(blank=True, default="", max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("group", models.ForeignKey(blank=True, help_text="Null = organisation-level default policy.", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="evaluation_policies", to="referentials.group")),
                ("organisation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="evaluation_policies", to="accounts.organisation")),
            ],
            options={
                "db_table": "evaluation_policy",
                "unique_together": {("organisation", "group")},
            },
        ),
        migrations.CreateModel(
            name="LearnerEvaluationRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("overall_status", models.CharField(choices=[("partial", "Partial"), ("complete", "Complete"), ("early_trigger", "Early trigger")], default="partial", max_length=32)),
                ("items", models.JSONField(default=list)),
                ("recap_text", models.TextField(blank=True, default="")),
                ("evaluation_profile_used", models.CharField(blank=True, default="", max_length=64)),
                ("shared_with_tutor", models.BooleanField(default=False)),
                ("tutor_validated", models.BooleanField(blank=True, null=True)),
                ("tutor_comment", models.TextField(blank=True, default="")),
                ("tutor_validated_at", models.DateTimeField(blank=True, null=True)),
                ("trigger_maturity", models.CharField(default="red", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("group", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="evaluation_records", to="referentials.group")),
                ("learner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="evaluation_records", to=settings.AUTH_USER_MODEL)),
                ("organisation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="learner_evaluation_records", to="accounts.organisation")),
                ("session", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="evaluation_record", to="hugo.hugosession")),
                ("tutor_validated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="validated_evaluation_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "learner_evaluation_record",
                "ordering": ["-created_at"],
            },
        ),
    ]

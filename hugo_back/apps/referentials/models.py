"""
Referentials: Group, GroupMembership, TutorLearnerLink, Referential, ReferentialItem,
Scale, ScaleLevel, ReferentialConfig, ReferentialItemOverlay.
"""
import uuid
from django.db import models
from django.conf import settings


class Group(models.Model):
    """Class / group (classe) — belongs to one organisation."""
    LLM_BACKENDS = [
        ("OLLAMA", "Ollama (local)"),
        ("OVH_AI", "OVH AI Endpoints"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="groups",
        null=False,
    )
    name = models.CharField(max_length=255)
    llm_backend = models.CharField(max_length=20, choices=LLM_BACKENDS, default="OLLAMA")
    default_tutor_prompt = models.ForeignKey(
        "hugo.TutorPrompt",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="groups_with_default_tutor_prompt",
        help_text="Legacy: single TutorPrompt default. Prefer default_learner_conversation_profile.",
    )
    default_learner_conversation_profile = models.ForeignKey(
        "hugo.LearnerConversationGlobalProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="groups_with_default_profile",
        help_text="Global learner conversation profile for this group.",
    )
    phase_classifier_enabled = models.BooleanField(
        null=True,
        blank=True,
        help_text="Optional override for phase classifier enablement at group level.",
    )
    phase_classifier_max_tokens = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional override for phase classifier max_tokens at group level.",
    )
    phase_classifier_min_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Optional override for phase classifier confidence threshold at group level (0..1).",
    )
    phase_classifier_max_input_chars = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional override for phase classifier input length cap at group level.",
    )
    p0_classifier_enabled = models.BooleanField(
        null=True,
        blank=True,
        help_text="Optional override for P0 classifier enablement at group level.",
    )
    p0_classifier_max_tokens = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional override for P0 classifier max_tokens at group level.",
    )
    p0_classifier_min_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Optional override for P0 classifier confidence threshold at group level (0..1).",
    )
    p0_classifier_max_input_chars = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional override for P0 classifier input length cap at group level.",
    )
    learner_display_profile = models.CharField(
        max_length=32,
        choices=[
            ("youth", "Youth"),
            ("adult", "Adult"),
            ("professional", "Professional"),
        ],
        default="professional",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "group"
        ordering = ["name"]

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    """User membership in a group (e.g. learner in class)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="group_memberships",
        null=False,
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="group_memberships",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "group_membership"
        unique_together = [["group", "user"]]
        ordering = ["-created_at"]


class TutorLearnerLink(models.Model):
    """Tutor/learner link scoped to a group (same org)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="tutor_learner_links",
        null=False,
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="tutor_learner_links",
        null=False,
    )
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_links",
    )
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learner_links",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tutor_learner_link"
        unique_together = [["group", "tutor", "learner"]]
        ordering = ["-created_at"]


class Scale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="scales",
        null=False,
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "scale"
        ordering = ["name"]


class ScaleLevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="scale_levels",
        null=False,
        blank=False,
    )
    scale = models.ForeignKey(Scale, on_delete=models.CASCADE, related_name="levels")
    level_order = models.PositiveSmallIntegerField(default=0)
    label = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "scale_level"
        ordering = ["scale", "level_order"]


class Referential(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="referentials",
        null=False,
    )
    name = models.CharField(max_length=255)
    source_ref = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "referential"
        ordering = ["name"]


class ReferentialItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="referential_items",
        null=False,
        blank=False,
    )
    referential = models.ForeignKey(
        Referential,
        on_delete=models.CASCADE,
        related_name="items",
    )
    code = models.CharField(max_length=128)
    title = models.CharField(max_length=512)
    block_code = models.CharField(max_length=64, blank=True, default="")
    block_label = models.CharField(max_length=255, blank=True, default="")
    evaluation_criteria = models.JSONField(default=list)
    evaluation_modalities = models.JSONField(default=list)
    expected_evidence = models.JSONField(default=list)
    source_ref = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "referential_item"
        unique_together = [["referential", "code"]]
        ordering = ["code"]


class ReferentialCriterion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="referential_criteria",
        null=False,
        blank=False,
    )
    referential_item = models.ForeignKey(
        ReferentialItem,
        on_delete=models.CASCADE,
        related_name="criteria",
    )
    code = models.CharField(max_length=128)
    label = models.CharField(max_length=512)
    order_index = models.PositiveIntegerField(default=0)
    expected_evidence = models.JSONField(default=list)
    question_seeds = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "referential_criterion"
        unique_together = [["referential_item", "code"]]
        ordering = ["referential_item", "order_index", "code"]


class ReferentialActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="referential_activities",
        null=False,
    )
    referential = models.ForeignKey(
        Referential,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    code = models.CharField(max_length=64)
    label = models.CharField(max_length=255)
    order_index = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "referential_activity"
        unique_together = [["referential", "code"]]
        ordering = ["referential", "order_index", "code"]


class ReferentialTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="referential_tasks",
        null=False,
    )
    activity = models.ForeignKey(
        ReferentialActivity,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    code = models.CharField(max_length=64)
    label = models.CharField(max_length=512)
    order_index = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "referential_task"
        unique_together = [["activity", "code"]]
        ordering = ["activity", "order_index", "code"]


class ReferentialCompetencyTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="referential_competency_tasks",
        null=False,
    )
    referential_item = models.ForeignKey(
        ReferentialItem,
        on_delete=models.CASCADE,
        related_name="competency_tasks",
    )
    task = models.ForeignKey(
        ReferentialTask,
        on_delete=models.CASCADE,
        related_name="competency_links",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "referential_competency_task"
        unique_together = [["referential_item", "task"]]
        ordering = ["-created_at"]


class ReferentialConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="referential_configs",
        null=False,
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="referential_configs",
    )
    referential = models.ForeignKey(
        Referential,
        on_delete=models.CASCADE,
        related_name="configs",
    )
    scale = models.ForeignKey(
        Scale,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referential_configs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "referential_config"
        unique_together = [["group", "referential"]]


class ReferentialItemOverlay(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="referential_item_overlays",
        null=False,
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="referential_item_overlays",
    )
    referential_item = models.ForeignKey(
        ReferentialItem,
        on_delete=models.CASCADE,
        related_name="overlays",
    )
    enabled = models.BooleanField(default=True)
    example_situations = models.JSONField(default=list)
    example_evidence = models.JSONField(default=list)
    common_mistakes = models.JSONField(default=list)
    coach_questions = models.JSONField(default=list)
    linked_documents = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "referential_item_overlay"
        unique_together = [["group", "referential_item"]]

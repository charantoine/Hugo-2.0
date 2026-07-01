"""
Hugo: sessions, messages, traces, evidence, learner_state.
All tables have organisation_id for RLS. No verbatim in logs.
"""
import uuid
from django.conf import settings
from django.db import models

from apps.hugo.domain.conversation_profile import ConversationPosture, KnowledgeItemStatus


class HugoConversationProfile(models.TextChoices):
    DIAGNOSTIC = ConversationPosture.DIAGNOSTIC.value, "Diagnostic"
    REFLECTIVE_AFEST = ConversationPosture.REFLECTIVE_AFEST.value, "Réflexif AFEST"
    KNOWLEDGE_REVIEW = ConversationPosture.KNOWLEDGE_REVIEW.value, "Savoirs / révision"


class OvhLlm(models.Model):
    """OVH LLM catalogue entry with simple pricing metadata."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    price_per_million_input = models.CharField(max_length=100)
    price_per_million_output = models.CharField(max_length=100)

    class Meta:
        db_table = "ovh_llm"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class StarterPrompt(models.Model):
    """Small preset questions exposed as starter buttons in the learner UI."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="starter_prompts",
        null=False,
    )
    button = models.CharField(max_length=255, help_text="Label du bouton affiché dans l’UI.")
    question = models.TextField(help_text="Question complète envoyée à l'apprenant quand il clique.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "starter_prompt"
        ordering = ["organisation_id", "button"]

    def __str__(self) -> str:
        return f"{self.organisation_id} / {self.button}"


class TutorPrompt(models.Model):
    """
    Configurable prompt for tutors / AFEST Hugo.

    Stores both raw templates (system/user) and structured parameters
    to steer the LLM behaviour.
    """

    class PromptType(models.TextChoices):
        AFEST_HUGO = "AFEST_HUGO", "AFEST Hugo"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="tutor_prompts",
        null=False,
    )
    code = models.SlugField(max_length=100)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    prompt_type = models.CharField(
        max_length=50,
        choices=PromptType.choices,
        default=PromptType.AFEST_HUGO,
    )
    is_default = models.BooleanField(
        default=False,
        help_text="If true, used as default for this organisation and prompt_type when no explicit prompt is set.",
    )

    # Optional profile code to link with SoT / prompt profiles in prompts/hugo/profiles/*.yaml
    sot_profile = models.CharField(max_length=100, blank=True)

    class SessionPhase(models.TextChoices):
        OPENING = "opening", "Opening"
        EXPLORATION = "exploration", "Exploration"
        DEEPENING = "deepening", "Deepening"
        POTENTIAL_CLOSURE = "potential_closure", "Potential closure"

    default_session_phase = models.CharField(
        max_length=32,
        choices=SessionPhase.choices,
        blank=True,
        help_text="Optional default session phase this prompt is optimized for.",
    )
    conversation_profile = models.CharField(
        max_length=32,
        choices=HugoConversationProfile.choices,
        default=HugoConversationProfile.REFLECTIVE_AFEST,
        help_text="Primary tutoring posture attached to this prompt.",
    )

    class OutputFormatMode(models.TextChoices):
        SINGLE_QUESTION = "single_question", "Single question"
        MULTI_QUESTION_NUMBERED = "multi_question_numbered", "Multiple questions, numbered"
        REFLECTION_BLOCK = "reflection_block", "Reflection block"

    output_format_mode = models.CharField(
        max_length=64,
        choices=OutputFormatMode.choices,
        default=OutputFormatMode.SINGLE_QUESTION,
    )

    # Raw templates with simple placeholders (e.g. {referential_block}, {learner_block}, {situation_content})
    system_template = models.TextField()
    user_template = models.TextField()

    class Language(models.TextChoices):
        FR = "fr", "Français"
        EN = "en", "English"

    language = models.CharField(
        max_length=8,
        choices=Language.choices,
        default=Language.FR,
    )

    class Tone(models.TextChoices):
        COACHING = "COACHING", "Coaching"
        NEUTRAL = "NEUTRAL", "Neutre"
        FRIENDLY = "FRIENDLY", "Amical"

    tone = models.CharField(
        max_length=20,
        choices=Tone.choices,
        default=Tone.COACHING,
    )

    ovh_llm = models.ForeignKey(
        OvhLlm,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tutor_prompts",
    )

    # Optional regulation biases (task / reasoning / metacognition) when TeachingPlan leaves room for interpretation.
    regulation_bias_task = models.FloatField(null=True, blank=True)
    regulation_bias_reasoning = models.FloatField(null=True, blank=True)
    regulation_bias_metacognition = models.FloatField(null=True, blank=True)

    max_questions_per_turn = models.PositiveIntegerField(default=1)
    max_tokens = models.PositiveIntegerField(
        default=150,
        help_text="Hint for the LLM client about the expected answer length.",
    )
    allow_lists = models.BooleanField(
        default=False,
        help_text="If false, templates should avoid requesting bulleted / numbered lists.",
    )

    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class PersonaScope(models.TextChoices):
        LEARNER = "learner", "Learner"
        TUTOR = "tutor", "Tutor"
        TRAINER = "trainer", "Trainer"

    persona_scope = models.CharField(
        max_length=16,
        choices=PersonaScope.choices,
        default=PersonaScope.LEARNER,
        help_text="Scope métier du prompt (apprenant vs persona tuteur/formateur).",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tutor_prompt"
        unique_together = [
            ["organisation", "prompt_type", "code"],
        ]
        ordering = ["organisation_id", "prompt_type", "code"]

    def __str__(self) -> str:
        return f"{self.organisation_id} / {self.prompt_type} / {self.code}"


class HugoSession(models.Model):
    """One reflective chat session (learner + group)."""
    class SessionPhase(models.TextChoices):
        OPENING = "opening", "Opening"
        EXPLORATION = "exploration", "Exploration"
        DEEPENING = "deepening", "Deepening"
        POTENTIAL_CLOSURE = "potential_closure", "Potential closure"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="hugo_sessions",
        null=False,
    )
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hugo_sessions",
    )
    group = models.ForeignKey(
        "referentials.Group",
        on_delete=models.CASCADE,
        related_name="hugo_sessions",
        null=True,
        blank=True,
    )
    tutor_prompt = models.ForeignKey(
        TutorPrompt,
        on_delete=models.SET_NULL,
        related_name="sessions",
        null=True,
        blank=True,
        help_text="Optional prompt configuration for this session. If empty, a suitable default will be used.",
    )
    learner_conversation_profile = models.ForeignKey(
        "LearnerConversationGlobalProfile",
        on_delete=models.SET_NULL,
        related_name="sessions",
        null=True,
        blank=True,
        help_text="Optional global learner conversation profile for this session.",
    )
    persona_conversation_profile = models.ForeignKey(
        "PersonaConversationProfile",
        on_delete=models.SET_NULL,
        related_name="sessions",
        null=True,
        blank=True,
        help_text="Optional persona profile (tuteur/formateur) for this session.",
    )
    current_phase = models.CharField(
        max_length=32,
        choices=SessionPhase.choices,
        default=SessionPhase.EXPLORATION,
        help_text="Current dialogue phase for this session.",
    )
    manual_phase_override = models.CharField(
        max_length=32,
        choices=SessionPhase.choices,
        blank=True,
        null=True,
        help_text="Optional manual override for phase progression.",
    )
    conversation_profile_override = models.CharField(
        max_length=32,
        choices=HugoConversationProfile.choices,
        blank=True,
        null=True,
        help_text="Optional conversation posture override for this session.",
    )
    posture = models.CharField(
        max_length=32,
        choices=HugoConversationProfile.choices,
        blank=True,
        default="",
        help_text="Resolved posture for the latest runtime turn.",
    )
    conversation_progress = models.JSONField(
        null=True,
        blank=True,
        default=None,
        help_text="Persisted product-safe conversation progress contract.",
    )
    analytics_state = models.JSONField(
        default=dict,
        blank=True,
        help_text="Aggregated runtime counters used for observability.",
    )
    phase_classifier_enabled = models.BooleanField(
        null=True,
        blank=True,
        help_text="Optional runtime override for phase classifier enablement.",
    )
    phase_classifier_max_tokens = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional runtime override for phase classifier max_tokens.",
    )
    phase_classifier_min_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Optional runtime override for phase classifier confidence threshold (0..1).",
    )
    phase_classifier_max_input_chars = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional runtime override for phase classifier input length cap.",
    )
    p0_classifier_enabled = models.BooleanField(
        null=True,
        blank=True,
        help_text="Optional runtime override for P0 classifier enablement.",
    )
    p0_classifier_max_tokens = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional runtime override for P0 classifier max_tokens.",
    )
    p0_classifier_min_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Optional runtime override for P0 classifier confidence threshold (0..1).",
    )
    p0_classifier_max_input_chars = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional runtime override for P0 classifier input length cap.",
    )
    # Sharing flags: false by default (privacy-first)
    share_summary = models.BooleanField(default=False)
    share_evidence = models.BooleanField(default=False)
    share_verbatim = models.BooleanField(default=False)
    evaluation_in_progress = models.BooleanField(
        default=False,
        help_text="True while an evaluation workflow is being prepared or reviewed.",
    )
    is_favorite = models.BooleanField(
        default=False,
        help_text="Learner-marked favorite for quick retrieval in the UI.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hugo_session"
        ordering = ["-created_at"]


class HugoMessage(models.Model):
    """One message in a session (learner or assistant). No raw content in logs."""
    class Role(models.TextChoices):
        LEARNER = "LEARNER", "Learner"
        ASSISTANT = "ASSISTANT", "Assistant"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="hugo_messages",
        null=False,
    )
    session = models.ForeignKey(
        HugoSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    assistant_display_variants = models.JSONField(default=dict, blank=True)
    # Optional LLM metadata for audit/debug (see llm_client).
    llm_request_payload = models.JSONField(default=dict, blank=True)
    llm_response_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hugo_message"
        ordering = ["created_at"]


class Trace(models.Model):
    """Structured trace (trace_rich_v1 payload) from a session."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="traces",
        null=False,
    )
    session = models.ForeignKey(
        HugoSession,
        on_delete=models.CASCADE,
        related_name="traces",
    )
    # referential_item can be added when we have referentials model
    referential_item_id = models.UUIDField(null=True, blank=True)
    payload_structured = models.JSONField(default=dict)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_traces",
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trace"
        ordering = ["-created_at"]


class TraceCriterionAssessment(models.Model):
    class CoverageStatus(models.TextChoices):
        NOT_SEEN = "not_seen", "Not seen"
        PARTIAL = "partial", "Partial"
        COVERED = "covered", "Covered"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="trace_criterion_assessments",
        null=False,
    )
    trace = models.ForeignKey(
        Trace,
        on_delete=models.CASCADE,
        related_name="criterion_assessments",
    )
    criterion = models.ForeignKey(
        "referentials.ReferentialCriterion",
        on_delete=models.CASCADE,
        related_name="trace_assessments",
    )
    status = models.CharField(
        max_length=20,
        choices=CoverageStatus.choices,
        default=CoverageStatus.PARTIAL,
    )
    confidence = models.FloatField(default=0.0)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trace_criterion_assessment"
        ordering = ["-created_at"]
        unique_together = [["trace", "criterion"]]


class Evidence(models.Model):
    """Photo/document evidence; must be linked to trace or session. EXIF stripped, GPS opt-in."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="evidence",
        null=False,
    )
    trace = models.ForeignKey(
        Trace,
        on_delete=models.CASCADE,
        related_name="evidence",
        null=True,
        blank=True,
    )
    session = models.ForeignKey(
        HugoSession,
        on_delete=models.CASCADE,
        related_name="evidence",
        null=True,
        blank=True,
    )
    file_path = models.CharField(max_length=512)
    meta = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "evidence"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(trace_id__isnull=False) | models.Q(session_id__isnull=False)),
                name="evidence_trace_or_session",
            )
        ]


class LearnerState(models.Model):
    """Cache: skills_matrix, missing_coverage, open_action_items, summary (recomputed on trace validation)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="learner_states",
        null=False,
    )
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learner_states",
    )
    group = models.ForeignKey(
        "referentials.Group",
        on_delete=models.CASCADE,
        related_name="learner_states",
        null=True,
        blank=True,
    )
    skills_matrix = models.JSONField(default=dict)
    missing_coverage = models.JSONField(default=list)
    open_action_items = models.JSONField(default=list)
    summary = models.TextField(blank=True, max_length=2000)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learner_state"
        ordering = ["-updated_at"]
        unique_together = [["learner", "group"]]


class LearnerThemeMemory(models.Model):
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="learner_theme_memories",
        null=False,
    )
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="theme_memories",
    )
    theme_key = models.CharField(max_length=256, db_index=True)
    referential_item_id = models.CharField(max_length=256, blank=True, default="")
    stabilised_points = models.JSONField(default=list)
    open_loops = models.JSONField(default=list)
    persistent_difficulties = models.JSONField(default=list)
    knowledge_status = models.CharField(
        max_length=32,
        choices=[(status.value, status.value) for status in KnowledgeItemStatus],
        default=KnowledgeItemStatus.DECLARED.value,
    )
    last_conversation = models.ForeignKey(
        HugoSession,
        on_delete=models.SET_NULL,
        related_name="theme_memory_records",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learner_theme_memory"
        ordering = ["-updated_at"]
        unique_together = [["learner", "organisation", "theme_key"]]

    def __str__(self) -> str:
        return f"{self.learner_id} / {self.theme_key}"


class TrainerKnowledgeItem(models.Model):
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="trainer_knowledge_items",
        null=False,
    )
    referential_item_id = models.CharField(max_length=256, blank=True, default="")
    content = models.TextField()
    content_type = models.CharField(max_length=64, default="mastery_criterion")
    source_type = models.CharField(max_length=64, default="declared")
    status = models.CharField(
        max_length=32,
        choices=[(status.value, status.value) for status in KnowledgeItemStatus],
        default=KnowledgeItemStatus.DECLARED.value,
    )
    confidence_score = models.FloatField(null=True, blank=True)
    provenance_note = models.TextField(blank=True, default="")
    meta = models.JSONField(default=dict, blank=True)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="validated_knowledge_items",
        null=True,
        blank=True,
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trainer_knowledge_item"
        ordering = ["-updated_at"]


class ConversationQualitySignal(models.Model):
    session = models.OneToOneField(
        HugoSession,
        on_delete=models.CASCADE,
        related_name="quality_signal",
    )
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="conversation_quality_signals",
        null=False,
    )
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversation_quality_signals",
    )
    posture = models.CharField(max_length=64, blank=True, default="")
    total_turns = models.IntegerField(default=0)
    active_branches_max = models.IntegerField(default=0)
    final_maturity = models.CharField(max_length=32, default="red")
    posture_switches = models.IntegerField(default=0)
    synthesis_requested = models.BooleanField(default=False)
    evaluation_requested = models.BooleanField(default=False)
    evaluation_was_eligible = models.BooleanField(default=False)
    dispersion_turns = models.IntegerField(default=0)
    stuck_red_turns = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conversation_quality_signal"
        ordering = ["-created_at"]


class TutorConductProfile(models.Model):
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="tutor_conduct_profiles",
        null=True,
        blank=True,
        help_text="Null = fallback system profile.",
    )
    posture = models.CharField(
        max_length=64,
        choices=HugoConversationProfile.choices,
        default=HugoConversationProfile.REFLECTIVE_AFEST,
    )
    system_template = models.TextField()
    user_template = models.TextField(blank=True, default="")
    max_questions_per_turn = models.PositiveSmallIntegerField(null=True, blank=True)
    forbidden_moves = models.JSONField(default=list, blank=True)
    allowed_moves = models.JSONField(default=list, blank=True)
    closure_policy = models.CharField(max_length=64, blank=True, default="")
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tutor_conduct_profile"
        ordering = ["posture", "organisation_id"]
        unique_together = [["organisation", "posture"]]

    def __str__(self) -> str:
        scope = self.organisation.name if self.organisation_id else "system"
        return f"{scope} / {self.posture}"


class EvaluationPromptProfile(models.Model):
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="evaluation_prompt_profiles",
        null=True,
        blank=True,
        help_text="Null = global fallback profile.",
    )
    code = models.CharField(max_length=64, db_index=True)
    label = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    prompt_frame = models.TextField()
    prompt_judgement_guide = models.TextField()
    prompt_output_guide = models.TextField()
    max_dialogue_turns = models.PositiveSmallIntegerField(default=6)
    ask_learner_confirmation = models.BooleanField(default=True)
    human_validation_required = models.BooleanField(default=True)
    updated_by = models.CharField(max_length=128, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "evaluation_prompt_profile"
        ordering = ["organisation_id", "code"]
        unique_together = [["organisation", "code"]]

    def __str__(self) -> str:
        scope = self.organisation.name if self.organisation_id else "platform"
        return f"[{scope}] {self.code} - {self.label}"


class LearnerConversationGlobalProfile(models.Model):
    """
    Global learner conversation profile grouping posture-specific prompts,
    conduct overrides and evaluation configuration for AFEST Hugo.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    POSTURE_PROMPT_FIELDS = {
        ConversationPosture.DIAGNOSTIC.value: "diagnostic_tutor_prompt",
        ConversationPosture.REFLECTIVE_AFEST.value: "reflective_tutor_prompt",
        ConversationPosture.KNOWLEDGE_REVIEW.value: "knowledge_review_tutor_prompt",
    }
    POSTURE_CONDUCT_FIELDS = {
        ConversationPosture.DIAGNOSTIC.value: "diagnostic_conduct_profile",
        ConversationPosture.REFLECTIVE_AFEST.value: "reflective_conduct_profile",
        ConversationPosture.KNOWLEDGE_REVIEW.value: "knowledge_review_conduct_profile",
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="learner_conversation_global_profiles",
        null=False,
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    is_default = models.BooleanField(
        default=False,
        help_text="If true, used as organisation default when no group/session profile is set.",
    )
    diagnostic_tutor_prompt = models.ForeignKey(
        TutorPrompt,
        on_delete=models.SET_NULL,
        related_name="global_profiles_diagnostic",
        null=True,
        blank=True,
    )
    reflective_tutor_prompt = models.ForeignKey(
        TutorPrompt,
        on_delete=models.SET_NULL,
        related_name="global_profiles_reflective",
        null=True,
        blank=True,
    )
    knowledge_review_tutor_prompt = models.ForeignKey(
        TutorPrompt,
        on_delete=models.SET_NULL,
        related_name="global_profiles_knowledge_review",
        null=True,
        blank=True,
    )
    diagnostic_conduct_profile = models.ForeignKey(
        TutorConductProfile,
        on_delete=models.SET_NULL,
        related_name="global_profiles_diagnostic_conduct",
        null=True,
        blank=True,
    )
    reflective_conduct_profile = models.ForeignKey(
        TutorConductProfile,
        on_delete=models.SET_NULL,
        related_name="global_profiles_reflective_conduct",
        null=True,
        blank=True,
    )
    knowledge_review_conduct_profile = models.ForeignKey(
        TutorConductProfile,
        on_delete=models.SET_NULL,
        related_name="global_profiles_knowledge_review_conduct",
        null=True,
        blank=True,
    )
    evaluation_prompt_profile = models.ForeignKey(
        "EvaluationPromptProfile",
        on_delete=models.SET_NULL,
        related_name="global_profiles_evaluation",
        null=True,
        blank=True,
    )
    evaluation_policy = models.ForeignKey(
        "EvaluationPolicy",
        on_delete=models.SET_NULL,
        related_name="global_profiles",
        null=True,
        blank=True,
        help_text="Optional organisation-level evaluation policy linked to this profile.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learner_conversation_global_profile"
        ordering = ["organisation_id", "name"]
        unique_together = [["organisation", "name"]]

    def __str__(self) -> str:
        return f"{self.organisation_id} / {self.name}"

    def get_tutor_prompt_for_posture(self, posture: str | None) -> TutorPrompt | None:
        posture_value = str(posture or ConversationPosture.REFLECTIVE_AFEST.value)
        field_name = self.POSTURE_PROMPT_FIELDS.get(posture_value)
        if not field_name:
            return None
        prompt = getattr(self, field_name, None)
        if prompt is not None and prompt.is_active:
            return prompt
        return None

    def get_conduct_profile_for_posture(self, posture: str | None) -> TutorConductProfile | None:
        posture_value = str(posture or ConversationPosture.REFLECTIVE_AFEST.value)
        field_name = self.POSTURE_CONDUCT_FIELDS.get(posture_value)
        if not field_name:
            return None
        profile = getattr(self, field_name, None)
        if profile is not None and profile.is_active:
            return profile
        return None


class PersonaConversationProfile(models.Model):
    """Profil conversationnel persona (tuteur ou formateur) — 1 prompt system/user."""

    class Persona(models.TextChoices):
        TUTOR = "tutor", "Tutor"
        TRAINER = "trainer", "Trainer"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="persona_conversation_profiles",
        null=False,
    )
    persona = models.CharField(max_length=16, choices=Persona.choices)
    code = models.SlugField(max_length=100)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Default persona profile for this organisation and persona kind.",
    )
    tutor_prompt = models.ForeignKey(
        TutorPrompt,
        on_delete=models.PROTECT,
        related_name="persona_profiles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "persona_conversation_profile"
        ordering = ["organisation_id", "persona", "name"]
        unique_together = [["organisation", "persona", "code"]]

    def __str__(self) -> str:
        return f"{self.organisation_id} / {self.persona} / {self.name}"


class EvaluationPolicy(models.Model):
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="evaluation_policies",
        null=False,
    )
    group = models.ForeignKey(
        "referentials.Group",
        on_delete=models.CASCADE,
        related_name="evaluation_policies",
        null=True,
        blank=True,
        help_text="Null = organisation-level default policy.",
    )
    share_with_tutor = models.BooleanField(default=True)
    tutor_validation_required = models.BooleanField(default=False)
    allow_early_trigger = models.BooleanField(default=True)
    early_trigger_warning = models.TextField(
        default="La conversation n'est pas encore suffisamment mûre. L'évaluation sera partielle.",
    )
    trainer_directives = models.TextField(blank=True, default="")
    evaluation_profile_code = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "evaluation_policy"
        unique_together = [["organisation", "group"]]


class LearnerEvaluationRecord(models.Model):
    class OverallStatus(models.TextChoices):
        PARTIAL = "partial", "Partial"
        COMPLETE = "complete", "Complete"
        EARLY_TRIGGER = "early_trigger", "Early trigger"

    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="learner_evaluation_records",
        null=False,
    )
    session = models.OneToOneField(
        HugoSession,
        on_delete=models.CASCADE,
        related_name="evaluation_record",
    )
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="evaluation_records",
    )
    group = models.ForeignKey(
        "referentials.Group",
        on_delete=models.SET_NULL,
        related_name="evaluation_records",
        null=True,
        blank=True,
    )
    overall_status = models.CharField(
        max_length=32,
        choices=OverallStatus.choices,
        default=OverallStatus.PARTIAL,
    )
    items = models.JSONField(default=list)
    recap_text = models.TextField(blank=True, default="")
    evaluation_profile_used = models.CharField(max_length=64, blank=True, default="")
    shared_with_tutor = models.BooleanField(default=False)
    tutor_validated = models.BooleanField(null=True, blank=True)
    tutor_comment = models.TextField(blank=True, default="")
    tutor_validated_at = models.DateTimeField(null=True, blank=True)
    tutor_validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="validated_evaluation_records",
        null=True,
        blank=True,
    )
    trigger_maturity = models.CharField(max_length=16, default="red")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learner_evaluation_record"
        ordering = ["-created_at"]


class ConversationTurnLLMAnalysis(models.Model):
    """D9bis — analyse dérivée par tour apprenant. Jamais verbatim ; export SUPERADMIN."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="conversation_turn_llm_analyses",
    )
    session = models.ForeignKey(
        HugoSession,
        on_delete=models.CASCADE,
        related_name="turn_llm_analyses",
    )
    learner_message = models.ForeignKey(
        HugoMessage,
        on_delete=models.CASCADE,
        related_name="turn_llm_analyses",
    )
    turn_index = models.PositiveIntegerField(default=1)
    analysis_version = models.CharField(max_length=32, default="d9bis_v1")
    quality_signals = models.JSONField(default=dict)
    pedagogical_tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conversation_turn_llm_analysis"
        ordering = ["session_id", "turn_index"]
        unique_together = [["session", "learner_message"]]


class ConversationLLMAnalysis(models.Model):
    """D9bis — agrégat analytique session. Canal technique séparé des exports métier."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        "accounts.Organisation",
        on_delete=models.CASCADE,
        related_name="conversation_llm_analyses",
    )
    session = models.OneToOneField(
        HugoSession,
        on_delete=models.CASCADE,
        related_name="llm_analysis",
    )
    analysis_version = models.CharField(max_length=32, default="d9bis_v1")
    turn_analyses_count = models.PositiveIntegerField(default=0)
    summary_metrics = models.JSONField(default=dict)
    export_scope = models.CharField(max_length=64, default="debug_superadmin_only")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conversation_llm_analysis"
        ordering = ["-created_at"]

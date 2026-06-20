from rest_framework import serializers
from django.core.files.storage import default_storage
from app_core.tenant_context import tenant_organisation_id
from .models import (
    EvaluationPolicy,
    EvaluationPromptProfile,
    HugoMessage,
    HugoSession,
    LearnerConversationGlobalProfile,
    LearnerEvaluationRecord,
    LearnerState,
    OvhLlm,
    StarterPrompt,
    Trace,
    Evidence,
    TutorConductProfile,
    TutorPrompt,
)


class OvhLlmSerializer(serializers.ModelSerializer):
    class Meta:
        model = OvhLlm
        fields = ["id", "name", "code", "description", "price_per_million_input", "price_per_million_output"]
        read_only_fields = ["id"]


class TutorPromptSerializer(serializers.ModelSerializer):
    ovh_llm = OvhLlmSerializer(read_only=True)
    ovh_llm_id = serializers.PrimaryKeyRelatedField(
        source="ovh_llm",
        queryset=OvhLlm.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = TutorPrompt
        fields = [
            "id",
            "organisation",
            "prompt_type",
            "code",
            "name",
            "description",
            "system_template",
            "user_template",
            "is_default",
            "is_active",
            "language",
            "tone",
            "output_format_mode",
            "sot_profile",
            "default_session_phase",
            "conversation_profile",
            "max_questions_per_turn",
            "max_tokens",
            "allow_lists",
            "ovh_llm",
            "ovh_llm_id",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "created_at", "updated_at", "ovh_llm"]


class HugoSessionSerializer(serializers.ModelSerializer):
    tutor_prompt = TutorPromptSerializer(read_only=True)
    first_learner_message = serializers.SerializerMethodField()
    effective_conversation_profile = serializers.SerializerMethodField()
    tutor_prompt_id = serializers.PrimaryKeyRelatedField(
        source="tutor_prompt",
        queryset=TutorPrompt.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = HugoSession
        fields = [
            "id",
            "learner",
            "group",
            "tutor_prompt",
            "tutor_prompt_id",
            "first_learner_message",
            "current_phase",
            "manual_phase_override",
            "conversation_profile_override",
            "effective_conversation_profile",
            "phase_classifier_enabled",
            "phase_classifier_max_tokens",
            "phase_classifier_min_confidence",
            "phase_classifier_max_input_chars",
            "p0_classifier_enabled",
            "p0_classifier_max_tokens",
            "p0_classifier_min_confidence",
            "p0_classifier_max_input_chars",
            "share_summary",
            "share_evidence",
            "share_verbatim",
            "is_favorite",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "learner",
            "created_at",
            "updated_at",
            "tutor_prompt",
            "current_phase",
            "manual_phase_override",
            "effective_conversation_profile",
            "phase_classifier_enabled",
            "phase_classifier_max_tokens",
            "phase_classifier_min_confidence",
            "phase_classifier_max_input_chars",
            "p0_classifier_enabled",
            "p0_classifier_max_tokens",
            "p0_classifier_min_confidence",
            "p0_classifier_max_input_chars",
        ]

    def get_first_learner_message(self, obj):
        content = getattr(obj, "first_learner_message_text", None)
        if content is None:
            first_msg = (
                obj.messages.filter(role=HugoMessage.Role.LEARNER)
                .order_by("created_at")
                .values_list("content", flat=True)
                .first()
            )
            content = first_msg or ""
        content = str(content or "").strip()
        if not content:
            return ""
        if len(content) > 120:
            return content[:117].rstrip() + "..."
        return content

    def get_effective_conversation_profile(self, obj):
        if getattr(obj, "conversation_profile_override", None):
            return obj.conversation_profile_override
        if getattr(obj, "tutor_prompt", None) and getattr(obj.tutor_prompt, "conversation_profile", None):
            return obj.tutor_prompt.conversation_profile
        return "reflective_afest"


class HugoSessionLearnerPatchSerializer(serializers.ModelSerializer):
    """Minimal PATCH payload for learners (e.g. favorite toggle)."""

    class Meta:
        model = HugoSession
        fields = ["is_favorite"]


class SessionClassifierConfigSerializer(serializers.Serializer):
    phase_classifier_enabled = serializers.BooleanField(required=False, allow_null=True)
    phase_classifier_max_tokens = serializers.IntegerField(required=False, allow_null=True)
    phase_classifier_min_confidence = serializers.FloatField(required=False, allow_null=True)
    phase_classifier_max_input_chars = serializers.IntegerField(required=False, allow_null=True)
    p0_classifier_enabled = serializers.BooleanField(required=False, allow_null=True)
    p0_classifier_max_tokens = serializers.IntegerField(required=False, allow_null=True)
    p0_classifier_min_confidence = serializers.FloatField(required=False, allow_null=True)
    p0_classifier_max_input_chars = serializers.IntegerField(required=False, allow_null=True)

    def validate_phase_classifier_min_confidence(self, value):
        if value is None:
            return value
        if value < 0 or value > 1:
            raise serializers.ValidationError("Must be between 0 and 1.")
        return value

    def validate_phase_classifier_max_tokens(self, value):
        if value is None:
            return value
        if value <= 0:
            raise serializers.ValidationError("Must be greater than 0.")
        return value

    def validate_phase_classifier_max_input_chars(self, value):
        if value is None:
            return value
        if value <= 0:
            raise serializers.ValidationError("Must be greater than 0.")
        return value

    def validate_p0_classifier_min_confidence(self, value):
        if value is None:
            return value
        if value < 0 or value > 1:
            raise serializers.ValidationError("Must be between 0 and 1.")
        return value

    def validate_p0_classifier_max_tokens(self, value):
        if value is None:
            return value
        if value <= 0:
            raise serializers.ValidationError("Must be greater than 0.")
        return value

    def validate_p0_classifier_max_input_chars(self, value):
        if value is None:
            return value
        if value <= 0:
            raise serializers.ValidationError("Must be greater than 0.")
        return value


class HugoMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HugoMessage
        fields = ["id", "session", "role", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class TraceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trace
        fields = [
            "id", "session", "referential_item_id", "payload_structured",
            "validated_by", "validated_at", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EvidenceSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        path = str(getattr(obj, "file_path", "") or "").strip()
        if not path:
            return ""
        try:
            return default_storage.url(path)
        except Exception:
            return ""

    class Meta:
        model = Evidence
        fields = ["id", "trace", "session", "file_path", "file_url", "meta", "created_at"]
        read_only_fields = ["id", "file_path", "created_at"]


class LearnerStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnerState
        fields = ["id", "learner", "group", "skills_matrix", "missing_coverage", "open_action_items", "summary", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class StarterPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = StarterPrompt
        fields = ["id", "organisation", "button", "question", "created_at", "updated_at"]
        read_only_fields = ["id", "organisation", "created_at", "updated_at"]


class TutorConductProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorConductProfile
        fields = [
            "id",
            "organisation",
            "posture",
            "system_template",
            "user_template",
            "max_questions_per_turn",
            "forbidden_moves",
            "allowed_moves",
            "closure_policy",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "created_at", "updated_at"]


class EvaluationPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationPolicy
        fields = [
            "id",
            "organisation",
            "group",
            "share_with_tutor",
            "tutor_validation_required",
            "allow_early_trigger",
            "early_trigger_warning",
            "trainer_directives",
            "evaluation_profile_code",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "created_at", "updated_at"]


class LearnerEvaluationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnerEvaluationRecord
        fields = [
            "id",
            "organisation",
            "session",
            "learner",
            "group",
            "overall_status",
            "items",
            "recap_text",
            "evaluation_profile_used",
            "shared_with_tutor",
            "tutor_validated",
            "tutor_comment",
            "tutor_validated_at",
            "tutor_validated_by",
            "trigger_maturity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "created_at", "updated_at"]


class EvaluationPromptProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationPromptProfile
        fields = [
            "id",
            "organisation",
            "code",
            "label",
            "is_active",
            "prompt_frame",
            "prompt_judgement_guide",
            "prompt_output_guide",
            "max_dialogue_turns",
            "ask_learner_confirmation",
            "human_validation_required",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "updated_by", "created_at", "updated_at"]


class LearnerConversationGlobalProfileSerializer(serializers.ModelSerializer):
    diagnostic_tutor_prompt_id = serializers.PrimaryKeyRelatedField(
        source="diagnostic_tutor_prompt",
        queryset=TutorPrompt.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    reflective_tutor_prompt_id = serializers.PrimaryKeyRelatedField(
        source="reflective_tutor_prompt",
        queryset=TutorPrompt.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    knowledge_review_tutor_prompt_id = serializers.PrimaryKeyRelatedField(
        source="knowledge_review_tutor_prompt",
        queryset=TutorPrompt.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    diagnostic_conduct_profile_id = serializers.PrimaryKeyRelatedField(
        source="diagnostic_conduct_profile",
        queryset=TutorConductProfile.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    reflective_conduct_profile_id = serializers.PrimaryKeyRelatedField(
        source="reflective_conduct_profile",
        queryset=TutorConductProfile.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    knowledge_review_conduct_profile_id = serializers.PrimaryKeyRelatedField(
        source="knowledge_review_conduct_profile",
        queryset=TutorConductProfile.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    evaluation_prompt_profile_id = serializers.PrimaryKeyRelatedField(
        source="evaluation_prompt_profile",
        queryset=EvaluationPromptProfile.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    evaluation_policy_id = serializers.PrimaryKeyRelatedField(
        source="evaluation_policy",
        queryset=EvaluationPolicy.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = LearnerConversationGlobalProfile
        fields = [
            "id",
            "organisation",
            "name",
            "description",
            "status",
            "is_default",
            "diagnostic_tutor_prompt",
            "diagnostic_tutor_prompt_id",
            "reflective_tutor_prompt",
            "reflective_tutor_prompt_id",
            "knowledge_review_tutor_prompt",
            "knowledge_review_tutor_prompt_id",
            "diagnostic_conduct_profile",
            "diagnostic_conduct_profile_id",
            "reflective_conduct_profile",
            "reflective_conduct_profile_id",
            "knowledge_review_conduct_profile",
            "knowledge_review_conduct_profile_id",
            "evaluation_prompt_profile",
            "evaluation_prompt_profile_id",
            "evaluation_policy",
            "evaluation_policy_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organisation",
            "diagnostic_tutor_prompt",
            "reflective_tutor_prompt",
            "knowledge_review_tutor_prompt",
            "diagnostic_conduct_profile",
            "reflective_conduct_profile",
            "knowledge_review_conduct_profile",
            "evaluation_prompt_profile",
            "evaluation_policy",
            "created_at",
            "updated_at",
        ]

    def _validate_org_fk(self, value, org_id, label: str):
        if value is None:
            return value
        fk_org_id = getattr(value, "organisation_id", None)
        if fk_org_id is not None and org_id and str(fk_org_id) != str(org_id):
            raise serializers.ValidationError(f"{label} must belong to the same organisation.")
        return value

    def _validate_tutor_prompt_posture(self, value, expected_posture: str, label: str):
        if value is None:
            return value
        actual = getattr(value, "conversation_profile", None)
        if actual and actual != expected_posture:
            raise serializers.ValidationError(
                f"{label} must have conversation_profile={expected_posture} (got {actual})."
            )
        return value

    def _validate_conduct_posture(self, value, expected_posture: str, label: str):
        if value is None:
            return value
        actual = getattr(value, "posture", None)
        if actual and actual != expected_posture:
            raise serializers.ValidationError(f"{label} must have posture={expected_posture} (got {actual}).")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        org_id = None
        if request is not None:
            org_id = tenant_organisation_id(request)
        elif self.instance is not None:
            org_id = self.instance.organisation_id

        slot_checks = [
            ("diagnostic_tutor_prompt", "diagnostic", "prompt"),
            ("reflective_tutor_prompt", "reflective_afest", "prompt"),
            ("knowledge_review_tutor_prompt", "knowledge_review", "prompt"),
            ("diagnostic_conduct_profile", "diagnostic", "conduct"),
            ("reflective_conduct_profile", "reflective_afest", "conduct"),
            ("knowledge_review_conduct_profile", "knowledge_review", "conduct"),
        ]
        for field, posture, kind in slot_checks:
            value = attrs.get(field)
            if value is None and self.instance is not None:
                value = getattr(self.instance, field, None)
            if kind == "prompt":
                self._validate_org_fk(value, org_id, field)
                self._validate_tutor_prompt_posture(value, posture, field)
            else:
                self._validate_org_fk(value, org_id, field)
                self._validate_conduct_posture(value, posture, field)

        for field in ("evaluation_prompt_profile", "evaluation_policy"):
            value = attrs.get(field)
            if value is None and self.instance is not None:
                value = getattr(self.instance, field, None)
            self._validate_org_fk(value, org_id, field)

        policy = attrs.get("evaluation_policy")
        if policy is None and self.instance is not None:
            policy = getattr(self.instance, "evaluation_policy", None)
        if policy is not None and getattr(policy, "group_id", None):
            raise serializers.ValidationError(
                {"evaluation_policy": "Only organisation-level policies (group=null) can be linked."}
            )

        return attrs

    def create(self, validated_data):
        org_id = validated_data.get("organisation_id") or validated_data["organisation"].id
        if validated_data.get("is_default"):
            LearnerConversationGlobalProfile.objects.filter(
                organisation_id=org_id,
                is_default=True,
            ).update(is_default=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("is_default"):
            LearnerConversationGlobalProfile.objects.filter(
                organisation_id=instance.organisation_id,
                is_default=True,
            ).exclude(id=instance.id).update(is_default=False)
        return super().update(instance, validated_data)

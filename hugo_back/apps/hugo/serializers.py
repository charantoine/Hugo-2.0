from rest_framework import serializers
from django.core.files.storage import default_storage
from app_core.tenant_context import tenant_organisation_id
from apps.hugo.services.session_profile_create import apply_session_profile_defaults
from .models import (
    EvaluationPolicy,
    EvaluationPromptProfile,
    HugoMessage,
    HugoSession,
    LearnerConversationGlobalProfile,
    LearnerEvaluationRecord,
    LearnerState,
    OvhLlm,
    PersonaConversationProfile,
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


        read_only_fields = ["id", "organisation", "created_at", "updated_at", "ovh_llm"]


class PersonaConversationProfileSerializer(serializers.ModelSerializer):
    tutor_prompt = TutorPromptSerializer(read_only=True)
    system_template = serializers.CharField(write_only=True, required=False, allow_blank=True)
    user_template = serializers.CharField(write_only=True, required=False, allow_blank=True)
    tutor_prompt_id = serializers.PrimaryKeyRelatedField(
        source="tutor_prompt",
        queryset=TutorPrompt.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = PersonaConversationProfile
        fields = [
            "id",
            "organisation",
            "persona",
            "code",
            "name",
            "description",
            "status",
            "is_default",
            "tutor_prompt",
            "tutor_prompt_id",
            "system_template",
            "user_template",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "created_at", "updated_at", "tutor_prompt"]

    def _persona_scope(self, persona: str) -> str:
        if persona == PersonaConversationProfile.Persona.TUTOR:
            return TutorPrompt.PersonaScope.TUTOR
        return TutorPrompt.PersonaScope.TRAINER

    def create(self, validated_data):
        system_template = validated_data.pop("system_template", None)
        user_template = validated_data.pop("user_template", None)
        tutor_prompt = validated_data.get("tutor_prompt")
        org = validated_data.get("organisation")
        if org is None:
            org_id = validated_data.pop("organisation_id", None)
            if org_id is not None:
                from apps.accounts.models import Organisation

                org = Organisation.objects.get(pk=org_id)
                validated_data["organisation"] = org
        persona = validated_data["persona"]
        code = validated_data["code"]

        if tutor_prompt is None:
            if not system_template or not user_template:
                raise serializers.ValidationError(
                    {"system_template": "Requis si tutor_prompt_id absent."}
                )
            tutor_prompt, _ = TutorPrompt.objects.update_or_create(
                organisation=org,
                prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
                code=code,
                defaults={
                    "name": validated_data.get("name") or code,
                    "system_template": system_template,
                    "user_template": user_template,
                    "persona_scope": self._persona_scope(persona),
                    "is_active": True,
                },
            )
            validated_data["tutor_prompt"] = tutor_prompt
        return super().create(validated_data)

    def update(self, instance, validated_data):
        system_template = validated_data.pop("system_template", None)
        user_template = validated_data.pop("user_template", None)
        instance = super().update(instance, validated_data)
        if system_template is not None or user_template is not None:
            prompt = instance.tutor_prompt
            if system_template is not None:
                prompt.system_template = system_template
            if user_template is not None:
                prompt.user_template = user_template
            prompt.persona_scope = self._persona_scope(instance.persona)
            prompt.save()
        return instance


class LearnerConversationGlobalProfileSummarySerializer(serializers.ModelSerializer):
    completeness = serializers.SerializerMethodField()

    class Meta:
        model = LearnerConversationGlobalProfile
        fields = ["id", "name", "description", "status", "is_default", "completeness"]
        read_only_fields = fields

    def get_completeness(self, obj):
        from apps.hugo.services.profile_completeness import compute_profile_completeness

        return compute_profile_completeness(obj)


class HugoSessionSerializer(serializers.ModelSerializer):
    tutor_prompt = TutorPromptSerializer(read_only=True)
    learner_conversation_profile = LearnerConversationGlobalProfileSummarySerializer(read_only=True)
    first_learner_message = serializers.SerializerMethodField()
    effective_conversation_profile = serializers.SerializerMethodField()
    resolved_conversation_profile_id = serializers.SerializerMethodField()
    tutor_prompt_id = serializers.PrimaryKeyRelatedField(
        source="tutor_prompt",
        queryset=TutorPrompt.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    learner_conversation_profile_id = serializers.PrimaryKeyRelatedField(
        source="learner_conversation_profile",
        queryset=LearnerConversationGlobalProfile.objects.filter(
            status=LearnerConversationGlobalProfile.Status.ACTIVE,
        ),
        write_only=True,
        required=False,
        allow_null=True,
    )
    persona_conversation_profile = PersonaConversationProfileSerializer(read_only=True)
    persona_conversation_profile_id = serializers.PrimaryKeyRelatedField(
        source="persona_conversation_profile",
        queryset=PersonaConversationProfile.objects.filter(
            status=PersonaConversationProfile.Status.ACTIVE,
        ),
        write_only=True,
        required=False,
        allow_null=True,
    )
    deprecation_warnings = serializers.SerializerMethodField()

    class Meta:
        model = HugoSession
        fields = [
            "id",
            "learner",
            "group",
            "tutor_prompt",
            "tutor_prompt_id",
            "learner_conversation_profile",
            "learner_conversation_profile_id",
            "persona_conversation_profile",
            "persona_conversation_profile_id",
            "resolved_conversation_profile_id",
            "deprecation_warnings",
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
            "learner_conversation_profile",
            "persona_conversation_profile",
            "resolved_conversation_profile_id",
            "deprecation_warnings",
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

    def get_resolved_conversation_profile_id(self, obj):
        from apps.hugo.services.learner_profile_resolver import resolve_learner_conversation_global_profile

        profile = resolve_learner_conversation_global_profile(obj)
        return str(profile.id) if profile is not None else None

    def get_deprecation_warnings(self, obj):
        warnings = []
        if getattr(obj, "tutor_prompt_id", None) and getattr(obj, "learner_conversation_profile_id", None):
            warnings.append("deprecated_session_tutor_prompt_with_global_profile")
        return warnings

    def validate(self, attrs):
        request = self.context.get("request")
        org_id = tenant_organisation_id(request) if request is not None else None
        profile = attrs.get("learner_conversation_profile")
        if profile is None and self.instance is not None:
            profile = getattr(self.instance, "learner_conversation_profile", None)
        if profile is not None and org_id and str(profile.organisation_id) != str(org_id):
            raise serializers.ValidationError(
                {"learner_conversation_profile_id": "Profile must belong to the same organisation."}
            )
        tutor_prompt = attrs.get("tutor_prompt")
        if tutor_prompt is not None and org_id and str(tutor_prompt.organisation_id) != str(org_id):
            raise serializers.ValidationError(
                {"tutor_prompt_id": "Tutor prompt must belong to the same organisation."}
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        org_id = tenant_organisation_id(request) if request is not None else None
        tutor_prompt_deprecated = "tutor_prompt" in validated_data
        try:
            validated_data = apply_session_profile_defaults(
                validated_data=validated_data,
                organisation_id=org_id,
                tutor_prompt_deprecated=tutor_prompt_deprecated,
            )
        except ValueError as exc:
            code = str(exc)
            if code == "inactive_learner_conversation_profile":
                raise serializers.ValidationError(
                    {"learner_conversation_profile_id": "Profile must be active."}
                ) from exc
            if code == "profile_org_mismatch":
                raise serializers.ValidationError(
                    {"learner_conversation_profile_id": "Profile must belong to the same organisation."}
                ) from exc
            raise
        self._create_deprecation_warnings = []
        if (
            tutor_prompt_deprecated
            and validated_data.get("tutor_prompt") is None
            and ("tutor_prompt_id" in self.initial_data or "tutor_prompt" in self.initial_data)
        ):
            self._create_deprecation_warnings.append("deprecated_tutor_prompt_id_ignored")
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        warnings = list(data.get("deprecation_warnings") or [])
        extra = getattr(self, "_create_deprecation_warnings", None)
        if extra:
            warnings.extend(extra)
        if warnings:
            data["deprecation_warnings"] = warnings
        return data


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

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance is not None:
            return attrs
        request = self.context.get("request")
        code = str(attrs.get("code") or "").strip()
        if not request or not code:
            return attrs
        org_id = tenant_organisation_id(request)
        if org_id and EvaluationPromptProfile.objects.filter(
            organisation_id=org_id,
            code=code,
        ).exists():
            raise serializers.ValidationError(
                {"code": "Un profil avec ce code existe déjà pour cette organisation."}
            )
        return attrs


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
    completeness = serializers.SerializerMethodField()
    missing_slots = serializers.SerializerMethodField()
    warnings = serializers.SerializerMethodField()

    class Meta:
        model = LearnerConversationGlobalProfile
        fields = [
            "id",
            "organisation",
            "name",
            "description",
            "status",
            "is_default",
            "completeness",
            "missing_slots",
            "warnings",
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
            "completeness",
            "missing_slots",
            "warnings",
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

    def _completeness_payload(self, obj):
        from apps.hugo.services.profile_completeness import compute_profile_completeness

        return compute_profile_completeness(obj)

    def get_completeness(self, obj):
        payload = self._completeness_payload(obj)
        return {
            "filled": payload["filled"],
            "total": payload["total"],
            "score": payload["score"],
        }

    def get_missing_slots(self, obj):
        return self._completeness_payload(obj)["missing_slots"]

    def get_warnings(self, obj):
        return self._completeness_payload(obj)["warnings"]

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

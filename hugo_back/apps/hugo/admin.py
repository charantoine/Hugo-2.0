"""Django admin for Hugo app."""
from django.contrib import admin
from .models import (
    EvaluationPolicy,
    EvaluationPromptProfile,
    OvhLlm,
    TutorPrompt,
    TutorConductProfile,
    StarterPrompt,
    HugoSession,
    HugoMessage,
    Trace,
    Evidence,
    LearnerState,
    LearnerEvaluationRecord,
)


@admin.register(OvhLlm)
class OvhLlmAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "price_per_million_input", "price_per_million_output"]
    search_fields = ["name", "code"]
    ordering = ["name"]


@admin.register(TutorPrompt)
class TutorPromptAdmin(admin.ModelAdmin):
    list_display = ["organisation", "prompt_type", "code", "name", "is_default", "is_active"]
    list_filter = ["organisation", "prompt_type", "is_default", "is_active", "language", "tone"]
    search_fields = ["code", "name", "description", "sot_profile"]
    save_as = True


@admin.register(StarterPrompt)
class StarterPromptAdmin(admin.ModelAdmin):
    list_display = ["organisation", "button", "question", "created_at"]
    search_fields = ["button", "question"]
    list_filter = ["organisation"]


@admin.register(HugoSession)
class HugoSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "organisation", "learner", "group", "tutor_prompt", "created_at"]
    list_filter = [
        "organisation",
        "group",
        "tutor_prompt",
        "is_favorite",
        "share_summary",
        "share_evidence",
        "share_verbatim",
    ]
    search_fields = ["id", "learner__username", "group__name"]
    date_hierarchy = "created_at"


@admin.register(HugoMessage)
class HugoMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "organisation", "session", "role", "created_at"]
    list_filter = ["organisation", "role"]
    search_fields = ["id", "session__id", "content"]
    date_hierarchy = "created_at"


@admin.register(Trace)
class TraceAdmin(admin.ModelAdmin):
    list_display = ["id", "organisation", "session", "validated_by", "validated_at", "created_at"]
    list_filter = ["organisation", "validated_at"]
    search_fields = ["id", "session__id"]
    date_hierarchy = "created_at"


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ["id", "organisation", "session", "trace", "file_path", "created_at"]
    list_filter = ["organisation"]
    search_fields = ["id", "file_path", "session__id", "trace__id"]
    date_hierarchy = "created_at"


@admin.register(LearnerState)
class LearnerStateAdmin(admin.ModelAdmin):
    list_display = ["id", "organisation", "learner", "group", "updated_at"]
    list_filter = ["organisation", "group"]
    search_fields = ["id", "learner__username", "group__name"]
    date_hierarchy = "updated_at"


@admin.register(TutorConductProfile)
class TutorConductProfileAdmin(admin.ModelAdmin):
    list_display = ["posture", "organisation", "is_active", "updated_at"]
    list_filter = ["posture", "organisation", "is_active"]
    search_fields = ["posture", "description", "system_template"]


@admin.register(EvaluationPromptProfile)
class EvaluationPromptProfileAdmin(admin.ModelAdmin):
    list_display = ["code", "organisation", "label", "is_active", "updated_by", "updated_at"]
    list_filter = ["is_active", "organisation"]
    search_fields = ["code", "label", "updated_by"]
    readonly_fields = ["created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        obj.updated_by = str(request.user)
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return bool(getattr(request.user, "is_superuser", False))

    def has_change_permission(self, request, obj=None):
        return bool(getattr(request.user, "is_superuser", False))

    def has_delete_permission(self, request, obj=None):
        return bool(getattr(request.user, "is_superuser", False))

    def has_view_permission(self, request, obj=None):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))


@admin.register(EvaluationPolicy)
class EvaluationPolicyAdmin(admin.ModelAdmin):
    list_display = ["organisation", "group", "share_with_tutor", "tutor_validation_required", "allow_early_trigger"]
    list_filter = ["organisation", "share_with_tutor", "tutor_validation_required", "allow_early_trigger"]
    search_fields = ["organisation__name", "group__name", "evaluation_profile_code"]


@admin.register(LearnerEvaluationRecord)
class LearnerEvaluationRecordAdmin(admin.ModelAdmin):
    list_display = ["session", "learner", "group", "overall_status", "shared_with_tutor", "tutor_validated", "created_at"]
    list_filter = ["organisation", "overall_status", "shared_with_tutor", "tutor_validated"]
    search_fields = ["session__id", "learner__username", "group__name", "evaluation_profile_used"]

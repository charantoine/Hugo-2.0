"""CRUD for LearnerConversationGlobalProfile (org-scoped)."""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from app_core.tenant_context import tenant_organisation_id
from apps.accounts.permissions import IsOrgAdminOrSuperadmin
from apps.hugo.models import LearnerConversationGlobalProfile
from apps.hugo.serializers import LearnerConversationGlobalProfileSerializer


class LearnerConversationGlobalProfileListCreate(generics.ListCreateAPIView):
    """GET/POST /hugo/learner-conversation-profiles/"""

    serializer_class = LearnerConversationGlobalProfileSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]

    def get_queryset(self):
        return (
            LearnerConversationGlobalProfile.objects.filter(
                organisation_id=tenant_organisation_id(self.request)
            )
            .select_related(
                "diagnostic_tutor_prompt",
                "reflective_tutor_prompt",
                "knowledge_review_tutor_prompt",
                "diagnostic_conduct_profile",
                "reflective_conduct_profile",
                "knowledge_review_conduct_profile",
                "evaluation_prompt_profile",
                "evaluation_policy",
            )
            .order_by("name")
        )

    def perform_create(self, serializer):
        serializer.save(organisation_id=tenant_organisation_id(self.request))


class LearnerConversationGlobalProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /hugo/learner-conversation-profiles/{id}/"""

    serializer_class = LearnerConversationGlobalProfileSerializer
    lookup_field = "id"

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]

    def get_queryset(self):
        return LearnerConversationGlobalProfile.objects.filter(
            organisation_id=tenant_organisation_id(self.request)
        ).select_related(
            "diagnostic_tutor_prompt",
            "reflective_tutor_prompt",
            "knowledge_review_tutor_prompt",
            "diagnostic_conduct_profile",
            "reflective_conduct_profile",
            "knowledge_review_conduct_profile",
            "evaluation_prompt_profile",
            "evaluation_policy",
        )

"""TutorPrompt CRUD for org admins."""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from app_core.tenant_context import tenant_organisation_id
from apps.accounts.permissions import IsOrgAdminOrSuperadmin
from .models import TutorPrompt
from .serializers import TutorPromptSerializer


class TutorPromptListCreate(generics.ListCreateAPIView):
    """GET/POST /hugo/tutor-prompts/ — list & create prompts for tenant organisation."""

    serializer_class = TutorPromptSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]

    def get_queryset(self):
        return TutorPrompt.objects.filter(organisation_id=tenant_organisation_id(self.request))

    def perform_create(self, serializer):
        serializer.save(organisation_id=tenant_organisation_id(self.request))


class TutorPromptDetail(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /hugo/tutor-prompts/{id}/ — manage a prompt of tenant organisation."""

    serializer_class = TutorPromptSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]
    lookup_field = "id"

    def get_queryset(self):
        return TutorPrompt.objects.filter(organisation_id=tenant_organisation_id(self.request))

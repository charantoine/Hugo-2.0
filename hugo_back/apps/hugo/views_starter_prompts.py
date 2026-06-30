"""StarterPrompt list for learners and CRUD for admins."""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from app_core.tenant_context import tenant_organisation_id
from apps.accounts.permissions import IsOrgAdminOrSuperadmin
from .models import StarterPrompt
from .serializers import StarterPromptSerializer


class StarterPromptListCreate(generics.ListCreateAPIView):
    """GET/POST /hugo/starter-prompts/ — list & create starter prompts for tenant organisation."""

    serializer_class = StarterPromptSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]

    def get_queryset(self):
        return StarterPrompt.objects.filter(organisation_id=tenant_organisation_id(self.request))

    def perform_create(self, serializer):
        serializer.save(organisation_id=tenant_organisation_id(self.request))


class StarterPromptDetail(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /hugo/starter-prompts/{id}/ — manage a starter prompt of tenant organisation."""

    serializer_class = StarterPromptSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]

    def get_queryset(self):
        return StarterPrompt.objects.filter(organisation_id=tenant_organisation_id(self.request))

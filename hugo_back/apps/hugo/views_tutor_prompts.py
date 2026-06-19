"""TutorPrompt CRUD for org admins."""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import TutorPrompt
from .serializers import TutorPromptSerializer
from apps.accounts.permissions import IsOrgAdminOrSuperadmin


class TutorPromptListCreate(generics.ListCreateAPIView):
    """GET/POST /hugo/tutor-prompts/ — list & create prompts for current organisation."""

    serializer_class = TutorPromptSerializer

    def get_permissions(self):
        # All authenticated users can GET the list (needed by learners to choose a prompt),
        # but only org admins / superadmins can create.
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]

    def get_queryset(self):
        return TutorPrompt.objects.filter(organisation_id=self.request.user.organisation_id)

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


class TutorPromptDetail(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /hugo/tutor-prompts/{id}/ — manage a prompt of current organisation."""

    serializer_class = TutorPromptSerializer

    def get_permissions(self):
        # Any authenticated user can read a prompt's details; only admins can modify/delete.
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]
    lookup_field = "id"

    def get_queryset(self):
        return TutorPrompt.objects.filter(organisation_id=self.request.user.organisation_id)


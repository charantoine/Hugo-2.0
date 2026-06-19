"""StarterPrompt list for learners and CRUD for admins."""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import StarterPrompt
from .serializers import StarterPromptSerializer
from apps.accounts.permissions import IsOrgAdminOrSuperadmin


class StarterPromptListCreate(generics.ListCreateAPIView):
    """GET/POST /hugo/starter-prompts/ — list & create starter prompts for current organisation."""

    serializer_class = StarterPromptSerializer

    def get_permissions(self):
        # Tous les utilisateurs authentifiés peuvent voir la liste (pour affichage dans l'UI),
        # mais seuls les admins/superadmins peuvent créer.
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]

    def get_queryset(self):
        return StarterPrompt.objects.filter(organisation_id=self.request.user.organisation_id)

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


class StarterPromptDetail(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /hugo/starter-prompts/{id}/ — manage a starter prompt of current organisation."""

    serializer_class = StarterPromptSerializer

    def get_permissions(self):
        # Lecture ouverte aux utilisateurs authentifiés; modifications réservées aux admins.
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]

    def get_queryset(self):
        return StarterPrompt.objects.filter(organisation_id=self.request.user.organisation_id)


"""OvhLlm CRUD for admin/superadmin (catalogue global, pas par organisation)."""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import OvhLlm
from .serializers import OvhLlmSerializer
from apps.accounts.permissions import IsOrgAdminOrSuperadmin


class OvhLlmListCreate(generics.ListCreateAPIView):
    """GET/POST /hugo/ovh-llms/ — list & create OVH LLM entries."""

    serializer_class = OvhLlmSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]
    queryset = OvhLlm.objects.all()


class OvhLlmDetail(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /hugo/ovh-llms/{id}/ — manage one OVH LLM entry."""

    serializer_class = OvhLlmSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]
    queryset = OvhLlm.objects.all()
    lookup_field = "id"

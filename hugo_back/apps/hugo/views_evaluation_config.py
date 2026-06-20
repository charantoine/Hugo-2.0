"""REST API for evaluation prompt profiles and org evaluation policies (admin)."""
from django.db.models import Q
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from app_core.tenant_context import tenant_organisation_id
from apps.accounts.permissions import IsOrgAdminOrSuperadmin
from apps.hugo.models import EvaluationPolicy, EvaluationPromptProfile
from apps.hugo.serializers import EvaluationPolicySerializer, EvaluationPromptProfileSerializer
from apps.referentials.access_control import is_superadmin


class EvaluationPromptProfileListCreate(generics.ListCreateAPIView):
    serializer_class = EvaluationPromptProfileSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]

    def get_queryset(self):
        org_id = tenant_organisation_id(self.request)
        return EvaluationPromptProfile.objects.filter(
            Q(organisation_id=org_id) | Q(organisation__isnull=True)
        ).order_by("organisation_id", "code")

    def perform_create(self, serializer):
        serializer.save(
            organisation_id=tenant_organisation_id(self.request),
            updated_by=self.request.user.username or "",
        )


class EvaluationPromptProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EvaluationPromptProfileSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]
    lookup_field = "id"

    def get_queryset(self):
        org_id = tenant_organisation_id(self.request)
        return EvaluationPromptProfile.objects.filter(
            Q(organisation_id=org_id) | Q(organisation__isnull=True)
        )

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.organisation_id is None and not is_superadmin(self.request.user):
            raise PermissionDenied("System evaluation profiles are read-only for organisation admins.")
        serializer.save(updated_by=self.request.user.username or "")

    def perform_destroy(self, instance):
        if instance.organisation_id is None and not is_superadmin(self.request.user):
            raise PermissionDenied("System evaluation profiles cannot be deleted by organisation admins.")
        instance.delete()


class EvaluationPolicyListCreate(generics.ListCreateAPIView):
    serializer_class = EvaluationPolicySerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]

    def get_queryset(self):
        org_id = tenant_organisation_id(self.request)
        return EvaluationPolicy.objects.select_related("group").filter(
            organisation_id=org_id
        ).order_by("group_id", "id")

    def perform_create(self, serializer):
        serializer.save(organisation_id=tenant_organisation_id(self.request))


class EvaluationPolicyDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EvaluationPolicySerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]
    lookup_field = "id"

    def get_queryset(self):
        org_id = tenant_organisation_id(self.request)
        return EvaluationPolicy.objects.filter(organisation_id=org_id)

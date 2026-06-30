from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from app_core.tenant_context import tenant_organisation_id
from apps.accounts.permissions import IsOrgAdminOrSuperadmin
from apps.hugo.models import TutorConductProfile
from apps.hugo.serializers import TutorConductProfileSerializer
from apps.referentials.access_control import is_superadmin


class TutorConductProfileListCreate(generics.ListCreateAPIView):
    serializer_class = TutorConductProfileSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]

    def get_queryset(self):
        org_id = tenant_organisation_id(self.request)
        return TutorConductProfile.objects.filter(
            Q(organisation_id=org_id) | Q(organisation__isnull=True)
        ).order_by("organisation_id", "posture")

    def perform_create(self, serializer):
        serializer.save(organisation_id=tenant_organisation_id(self.request))


class TutorConductProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TutorConductProfileSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]
    lookup_field = "id"

    def get_queryset(self):
        org_id = tenant_organisation_id(self.request)
        return TutorConductProfile.objects.filter(
            Q(organisation_id=org_id) | Q(organisation__isnull=True)
        )

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.organisation_id is None and not is_superadmin(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("System profiles are read-only for organisation admins.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.organisation_id is None and not is_superadmin(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("System profiles cannot be deleted by organisation admins.")
        instance.delete()

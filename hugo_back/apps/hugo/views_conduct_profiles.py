from rest_framework import generics
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsOrgAdminOrSuperadmin
from apps.hugo.models import TutorConductProfile
from apps.hugo.serializers import TutorConductProfileSerializer


class TutorConductProfileListCreate(generics.ListCreateAPIView):
    serializer_class = TutorConductProfileSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_superuser", False):
            return TutorConductProfile.objects.all().order_by("organisation_id", "posture")
        return TutorConductProfile.objects.filter(
            Q(organisation_id=user.organisation_id) | Q(organisation__isnull=True)
        ).order_by("organisation_id", "posture")

    def perform_create(self, serializer):
        serializer.save(organisation=self.request.user.organisation)


class TutorConductProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TutorConductProfileSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_superuser", False):
            return TutorConductProfile.objects.all()
        return TutorConductProfile.objects.filter(Q(organisation_id=user.organisation_id) | Q(organisation__isnull=True))

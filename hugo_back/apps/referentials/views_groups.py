"""Groups API: POST/GET /groups, POST /groups/{id}/members, POST /groups/{id}/tutor-links."""
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Role
from .models import Group, GroupMembership, TutorLearnerLink
from .serializers import GroupSerializer, GroupMembershipSerializer, TutorLearnerLinkSerializer
from apps.accounts.permissions import IsOrgAdminOrSuperadmin
from .access_control import is_admin_like, is_tutor_like


class GroupListCreate(generics.ListCreateAPIView):
    """POST/GET /groups — list/create groups for current org."""

    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        org_id = self.request.user.organisation_id
        qs = Group.objects.filter(organisation_id=org_id)
        if is_admin_like(self.request.user):
            return qs
        if is_tutor_like(self.request.user):
            tutor_group_ids = GroupMembership.objects.filter(
                organisation_id=org_id,
                user_id=self.request.user.id,
            ).values_list("group_id", flat=True)
            linked_group_ids = TutorLearnerLink.objects.filter(
                organisation_id=org_id,
                tutor_id=self.request.user.id,
            ).values_list("group_id", flat=True)
            return qs.filter(id__in=tutor_group_ids).filter(id__in=linked_group_ids).distinct()
        return qs.filter(
            memberships__organisation_id=org_id,
            memberships__user_id=self.request.user.id,
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


class GroupRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """GET/PATCH /groups/{group_id}/ — detail & update for current org (admin/superadmin)."""

    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]
    lookup_url_kwarg = "group_id"
    lookup_field = "id"

    def get_queryset(self):
        return Group.objects.filter(organisation_id=self.request.user.organisation_id)


class GroupMembershipListCreate(generics.ListCreateAPIView):
    """POST/GET /groups/{group_id}/members — add/list members."""
    serializer_class = GroupMembershipSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return GroupMembership.objects.filter(
            group_id=self.kwargs["group_id"],
            organisation_id=self.request.user.organisation_id,
        )

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if not user:
            raise ValidationError("user is required.")
        if str(user.organisation_id) != str(self.request.user.organisation_id):
            raise ValidationError("User must belong to the current organisation.")
        if user.role not in {Role.LEARNER, Role.TUTOR, Role.TRAINER, Role.COORDO}:
            raise ValidationError("Only learner or tutor-like accounts can be attached to a group.")
        serializer.save(
            group_id=self.kwargs["group_id"],
            organisation_id=self.request.user.organisation_id,
        )


class TutorLinkListCreate(generics.ListCreateAPIView):
    """POST/GET /groups/{group_id}/tutor-links — add/list tutor-learner links."""
    serializer_class = TutorLearnerLinkSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        org_id = self.request.user.organisation_id
        group_id = self.kwargs["group_id"]
        qs = TutorLearnerLink.objects.filter(
            organisation_id=self.request.user.organisation_id,
            group_id=group_id,
        )
        if is_admin_like(self.request.user):
            return qs
        if is_tutor_like(self.request.user):
            return qs.filter(tutor_id=self.request.user.id)
        return qs.filter(learner_id=self.request.user.id)

    def perform_create(self, serializer):
        group_id = self.kwargs["group_id"]
        org_id = self.request.user.organisation_id
        tutor = serializer.validated_data.get("tutor")
        learner = serializer.validated_data.get("learner")
        tutor_id = getattr(tutor, "id", tutor)
        learner_id = getattr(learner, "id", learner)
        if not is_admin_like(self.request.user) and str(tutor_id) != str(self.request.user.id):
            raise ValidationError("Only admins can assign links for another tutor.")
        tutor_in_group = GroupMembership.objects.filter(
            group_id=group_id,
            organisation_id=org_id,
            user_id=tutor_id,
        ).exists()
        learner_in_group = GroupMembership.objects.filter(
            group_id=group_id,
            organisation_id=org_id,
            user_id=learner_id,
        ).exists()
        if not tutor_in_group or not learner_in_group:
            raise ValidationError("Tutor and learner must both belong to this group.")
        serializer.save(organisation_id=org_id, group_id=group_id)

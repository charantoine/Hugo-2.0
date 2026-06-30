"""Groups API: POST/GET /groups, POST /groups/{id}/members, POST /groups/{id}/tutor-links."""
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from app_core.tenant_context import get_group_for_tenant, tenant_organisation_id
from apps.accounts.models import Role
from apps.accounts.permissions import IsOrgAdminOrSuperadmin, IsSuperadmin
from apps.quality.views import log_audit
from .access_control import is_admin_like, is_superadmin, is_tutor_like
from .models import Group, GroupMembership, TutorLearnerLink
from .serializers import GroupSerializer, GroupMembershipSerializer, TutorLearnerLinkSerializer


class GroupListCreate(generics.ListCreateAPIView):
    """POST/GET /groups — list/create groups for tenant organisation."""

    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        org_id = tenant_organisation_id(self.request)
        qs = Group.objects.filter(organisation_id=org_id)
        user = self.request.user
        role = getattr(user, "role", None)
        if is_admin_like(user):
            return qs
        # Formateurs : accès org-wide à la bibliothèque (cf. library._can_read_group_library).
        if role == Role.TRAINER:
            return qs
        if is_tutor_like(user):
            tutor_group_ids = GroupMembership.objects.filter(
                organisation_id=org_id,
                user_id=user.id,
            ).values_list("group_id", flat=True)
            linked_group_ids = TutorLearnerLink.objects.filter(
                organisation_id=org_id,
                tutor_id=user.id,
            ).values_list("group_id", flat=True)
            return qs.filter(id__in=tutor_group_ids).filter(id__in=linked_group_ids).distinct()
        return qs.filter(
            memberships__organisation_id=org_id,
            memberships__user_id=user.id,
        ).distinct()

    def perform_create(self, serializer):
        org_id = tenant_organisation_id(self.request)
        group = serializer.save(organisation_id=org_id)
        log_audit(self.request, "group_created", "group", group.id)


class GroupRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """GET/PATCH /groups/{group_id}/ — detail & update for tenant org (admin/superadmin)."""

    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]
    lookup_url_kwarg = "group_id"
    lookup_field = "id"

    def get_queryset(self):
        org_id = tenant_organisation_id(self.request)
        return Group.objects.filter(organisation_id=org_id)


class GroupMembershipListCreate(generics.ListCreateAPIView):
    """POST/GET /groups/{group_id}/members — add/list members."""

    serializer_class = GroupMembershipSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsOrgAdminOrSuperadmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        org_id = tenant_organisation_id(self.request)
        return GroupMembership.objects.filter(
            group_id=self.kwargs["group_id"],
            organisation_id=org_id,
        ).select_related("user")

    def perform_create(self, serializer):
        group = get_group_for_tenant(self.request, self.kwargs["group_id"])
        user = serializer.validated_data.get("user")
        if not user:
            raise ValidationError("user is required.")
        if str(user.organisation_id) != str(group.organisation_id):
            raise ValidationError("User must belong to the same organisation as the group.")
        if user.role not in {Role.LEARNER, Role.TUTOR, Role.TRAINER, Role.COORDO}:
            raise ValidationError("Only learner or tutor-like accounts can be attached to a group.")
        membership = serializer.save(
            group_id=group.id,
            organisation_id=group.organisation_id,
        )
        log_audit(self.request, "group_membership_created", "group_membership", membership.id)


class TutorLinkListCreate(generics.ListCreateAPIView):
    """
    POST/GET /groups/{group_id}/tutor-links — tutor-learner links.

    Transitional policy (2026-06): POST restricted to SUPERADMIN only.
    ORGADMIN will be enabled later alongside SUPERADMIN.
    """

    serializer_class = TutorLearnerLinkSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsSuperadmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        org_id = tenant_organisation_id(self.request)
        group_id = self.kwargs["group_id"]
        qs = TutorLearnerLink.objects.filter(
            organisation_id=org_id,
            group_id=group_id,
        )
        if is_superadmin(self.request.user):
            return qs
        if is_tutor_like(self.request.user):
            return qs.filter(tutor_id=self.request.user.id)
        return qs.filter(learner_id=self.request.user.id)

    def perform_create(self, serializer):
        group = get_group_for_tenant(self.request, self.kwargs["group_id"])
        group_id = group.id
        org_id = group.organisation_id
        tutor = serializer.validated_data.get("tutor")
        learner = serializer.validated_data.get("learner")
        tutor_id = getattr(tutor, "id", tutor)
        learner_id = getattr(learner, "id", learner)
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
        link = serializer.save(organisation_id=org_id, group_id=group_id)
        log_audit(self.request, "tutor_learner_link_created", "tutor_learner_link", link.id)

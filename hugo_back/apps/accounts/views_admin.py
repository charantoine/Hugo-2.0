"""Admin views: create organisations, create users (POC manual)."""
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app_core.tenant_context import tenant_organisation_id
from apps.quality.views import log_audit

from .models import Organisation, Role, User
from .serializers import OrganisationSerializer, UserAdminUpdateSerializer, UserCreateSerializer, UserListSerializer
from .permissions import IsOrgAdminOrSuperadmin


class OrganisationCreateList(generics.ListCreateAPIView):
    """POST/GET /admin/organisations — ORGADMIN/SUPERADMIN."""

    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]

    def get_queryset(self):
        qs = Organisation.objects.all()
        if self.request.user.role == Role.ORGADMIN:
            qs = qs.filter(id=self.request.user.organisation_id)
        return qs

    def perform_create(self, serializer):
        org = serializer.save()
        log_audit(self.request, "organisation_created", "organisation", org.id)


class OrganisationDetail(generics.RetrieveUpdateAPIView):
    """GET/PATCH /admin/organisations/{org_id}/ — SUPERADMIN any org, ORGADMIN own org."""

    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]
    lookup_url_kwarg = "org_id"
    lookup_field = "id"

    def get_queryset(self):
        qs = Organisation.objects.all()
        if self.request.user.role == Role.ORGADMIN:
            qs = qs.filter(id=self.request.user.organisation_id)
        return qs


class UserCreate(generics.CreateAPIView):
    """POST /admin/users — create user in org (manual POC, backoffice)."""

    serializer_class = UserCreateSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_audit(request, "user_created", "user", user.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrgUserCreate(generics.ListCreateAPIView):
    """GET/POST /users — list + create users in tenant organisation for admin/superadmin."""

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserListSerializer
        return UserCreateSerializer

    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]

    def get_queryset(self):
        org_id = tenant_organisation_id(self.request)
        if not org_id:
            return User.objects.none()
        return User.objects.filter(organisation_id=org_id)

    def get_serializer(self, *args, **kwargs):
        """
        Inject tenant organisation if not provided explicitly.
        Frontend only sends username, email, password, role.
        """
        data = kwargs.get("data")
        org_id = tenant_organisation_id(self.request)
        if isinstance(data, dict) and "organisation" not in data and org_id:
            payload = data.copy()
            payload["organisation"] = org_id
            kwargs["data"] = payload
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        user = serializer.save()
        log_audit(self.request, "user_created", "user", user.id)


class OrgUserDetail(generics.RetrieveUpdateAPIView):
    """GET/PATCH /users/{user_id}/ — user detail/update in tenant organisation."""

    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]
    lookup_url_kwarg = "user_id"
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return UserAdminUpdateSerializer
        return UserListSerializer

    def get_queryset(self):
        org_id = tenant_organisation_id(self.request)
        if not org_id:
            return User.objects.none()
        return User.objects.filter(organisation_id=org_id)

    def perform_update(self, serializer):
        if "organisation" in serializer.validated_data:
            raise PermissionDenied("Transferring users between organisations is forbidden.")
        previous_role = serializer.instance.role
        user = serializer.save()
        if user.role != previous_role:
            log_audit(self.request, "user_role_changed", "user", user.id)

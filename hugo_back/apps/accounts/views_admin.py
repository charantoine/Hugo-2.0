"""Admin views: create organisations, create users (POC manual)."""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Organisation, User
from .serializers import OrganisationSerializer, UserAdminUpdateSerializer, UserCreateSerializer, UserListSerializer
from .permissions import IsOrgAdminOrSuperadmin


class OrganisationCreateList(generics.ListCreateAPIView):
    """POST/GET /admin/organisations — ORGADMIN/SUPERADMIN."""
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]

    def get_queryset(self):
        qs = Organisation.objects.all()
        if self.request.user.role == "ORGADMIN":
            qs = qs.filter(id=self.request.user.organisation_id)
        return qs


class UserCreate(generics.CreateAPIView):
    """POST /admin/users — create user in org (manual POC, backoffice)."""

    serializer_class = UserCreateSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrgUserCreate(generics.ListCreateAPIView):
    """GET/POST /users — list + create users in current organisation for admin/superadmin (frontend)."""

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserListSerializer
        return UserCreateSerializer
    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]

    def get_queryset(self):
        """Limit listing to current organisation."""
        qs = User.objects.all()
        org_id = getattr(self.request.user, "organisation_id", None)
        if org_id:
            qs = qs.filter(organisation_id=org_id)
        return qs

    def get_serializer(self, *args, **kwargs):
        """
        Inject the current organisation if not provided explicitly.
        Frontend only sends username, email, password, role.
        """
        data = kwargs.get("data")
        if isinstance(data, dict) and "organisation" not in data and getattr(
            self.request.user, "organisation_id", None
        ):
            payload = data.copy()
            payload["organisation"] = self.request.user.organisation_id
            kwargs["data"] = payload
        return super().get_serializer(*args, **kwargs)


class OrgUserDetail(generics.RetrieveUpdateAPIView):
    """GET/PATCH /users/{user_id}/ — user detail/update in current organisation (admin/superadmin)."""

    permission_classes = [IsAuthenticated, IsOrgAdminOrSuperadmin]
    lookup_url_kwarg = "user_id"
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return UserAdminUpdateSerializer
        return UserListSerializer

    def get_queryset(self):
        qs = User.objects.all()
        org_id = getattr(self.request.user, "organisation_id", None)
        if org_id:
            qs = qs.filter(organisation_id=org_id)
        return qs


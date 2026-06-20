"""
Tenant organisation context — single source of truth for org scoping.

SUPERADMIN may send ``X-Organisation-Id`` to operate in another organisation.
All other roles are always scoped to their home organisation (header ignored).
"""
from __future__ import annotations

import logging
from uuid import UUID

from django.db import connection
from django.shortcuts import get_object_or_404

from apps.accounts.models import Organisation, Role
from apps.referentials.access_control import is_superadmin

logger = logging.getLogger(__name__)

ORG_CONTEXT_HEADER = "X-Organisation-Id"


def _parse_uuid(value) -> UUID | None:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return None


def _django_request(request):
    return getattr(request, "_request", request)


def _authenticated_user(request):
    req = _django_request(request)
    user = getattr(req, "user", None)
    if user and getattr(user, "is_authenticated", False):
        return user
    return None


def home_organisation_id(request) -> UUID | None:
    user = _authenticated_user(request)
    if not user:
        return None
    org_id = getattr(user, "organisation_id", None)
    if org_id is None and hasattr(user, "organisation"):
        org_id = getattr(user.organisation, "id", None)
    return _parse_uuid(org_id)


def _requested_organisation_id(request) -> UUID | None:
    req = _django_request(request)
    raw = req.META.get("HTTP_X_ORGANISATION_ID")
    if not raw and hasattr(req, "headers"):
        raw = req.headers.get(ORG_CONTEXT_HEADER)
    return _parse_uuid(raw)


def resolve_effective_organisation_id(request, user=None) -> UUID | None:
    """
    Resolve tenant org for the authenticated user.
    Raises ValueError when SUPERADMIN sends an unknown organisation id.
    """
    user = user or _authenticated_user(request)
    if not user:
        return None

    home_id = _parse_uuid(getattr(user, "organisation_id", None))
    if home_id is None and hasattr(user, "organisation"):
        home_id = _parse_uuid(getattr(user.organisation, "id", None))
    if home_id is None:
        return None

    requested_id = _requested_organisation_id(request)
    if requested_id is None:
        return home_id

    if getattr(user, "role", None) != Role.SUPERADMIN:
        return home_id

    if requested_id == home_id:
        return home_id

    if not Organisation.objects.filter(id=requested_id).exists():
        raise ValueError(f"Unknown organisation id: {requested_id}")

    return requested_id


def _set_rls(organisation_id: UUID | None) -> None:
    if organisation_id is None:
        return
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SET LOCAL app.organisation_id = %s",
                [str(organisation_id)],
            )
    except Exception as exc:
        logger.warning(
            "tenant_rls_failed",
            extra={"organisation_id": str(organisation_id), "error": str(exc)},
        )


def bind_tenant_context(request, user=None) -> UUID | None:
    """Bind effective organisation on request and set PostgreSQL RLS variable."""
    req = _django_request(request)
    org_id = resolve_effective_organisation_id(req, user=user)
    req.effective_organisation_id = org_id
    _set_rls(org_id)
    return org_id


def tenant_organisation_id(request) -> UUID | None:
    """
    Effective tenant org for this request.
    Lazily binds tenant context (JWT auth happens after Django middleware).
    """
    req = _django_request(request)
    existing = getattr(req, "effective_organisation_id", None)
    if existing is not None:
        return _parse_uuid(existing)

    user = _authenticated_user(request)
    if not user:
        return None

    try:
        org_id = resolve_effective_organisation_id(req, user=user)
    except ValueError as exc:
        from rest_framework.exceptions import ValidationError

        raise ValidationError(str(exc)) from exc

    req.effective_organisation_id = org_id
    _set_rls(org_id)
    return org_id


def assert_tenant_access(request, target_org_id) -> None:
    """Ensure caller operates inside the effective tenant organisation."""
    from rest_framework.exceptions import PermissionDenied

    target = _parse_uuid(target_org_id)
    effective = tenant_organisation_id(request)
    if target is None or effective is None:
        raise PermissionDenied("Organisation context required.")
    if str(target) != str(effective):
        raise PermissionDenied("Cross-organisation access denied.")
    if not is_superadmin(_authenticated_user(request)):
        home = home_organisation_id(request)
        if str(home) != str(effective):
            raise PermissionDenied("Cross-organisation access denied.")


def get_group_for_tenant(request, group_id):
    from apps.referentials.models import Group

    org_id = tenant_organisation_id(request)
    return get_object_or_404(Group, id=group_id, organisation_id=org_id)


def try_bind_tenant_from_jwt(request) -> None:
    """Best-effort early bind for JWT requests (before DRF view dispatch)."""
    if _authenticated_user(request):
        bind_tenant_context(request)
        return
    try:
        from rest_framework.request import Request
        from rest_framework_simplejwt.authentication import JWTAuthentication

        drf_request = Request(request)
        auth_result = JWTAuthentication().authenticate(drf_request)
        if not auth_result:
            return
        user, _token = auth_result
        request.user = user
        bind_tenant_context(request, user=user)
    except Exception:
        return

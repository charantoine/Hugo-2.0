"""
Tenant RLS middleware — sets app.organisation_id for the current request.
Runs AFTER authentication, BEFORE any ORM query.
SPEC: SET LOCAL app.organisation_id = %s per transaction.
"""
import logging
from uuid import UUID

from django.db import connection

logger = logging.getLogger(__name__)


class TenantRLSMiddleware:
    """
    Set PostgreSQL session variable app.organisation_id from the authenticated user's org.
    Must be placed after AuthenticationMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._set_tenant(request)
        return self.get_response(request)

    def _set_tenant(self, request):
        organisation_id = self._get_organisation_id(request)
        if organisation_id is None:
            return
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SET LOCAL app.organisation_id = %s",
                    [str(organisation_id)],
                )
        except Exception as e:
            logger.warning(
                "tenant_rls_failed",
                extra={
                    "organisation_id": str(organisation_id),
                    "error": str(e),
                },
            )

    def _get_organisation_id(self, request):
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return None
        user = request.user
        org_id = getattr(user, "organisation_id", None)
        if org_id is None and hasattr(user, "organisation"):
            org_id = getattr(user.organisation, "id", None)
        if org_id is not None and not isinstance(org_id, UUID):
            try:
                org_id = UUID(str(org_id))
            except (ValueError, TypeError):
                return None
        return org_id

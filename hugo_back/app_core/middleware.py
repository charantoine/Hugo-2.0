"""
Tenant RLS middleware — sets app.organisation_id for the current request.
Runs AFTER authentication, attempts early JWT bind before ORM access.
"""
import logging

from django.db import connection
from django.http import JsonResponse

from app_core.tenant_context import bind_tenant_context, try_bind_tenant_from_jwt

logger = logging.getLogger(__name__)


class TenantRLSMiddleware:
    """
    Bind tenant context from session user or JWT, then set PostgreSQL RLS variable.
    Must be placed after AuthenticationMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        error_response = self._bind_tenant_context(request)
        if error_response is not None:
            return error_response
        return self.get_response(request)

    def _bind_tenant_context(self, request):
        request.effective_organisation_id = None
        try_bind_tenant_from_jwt(request)
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return None
        try:
            bind_tenant_context(request, user=request.user)
        except ValueError as exc:
            return JsonResponse({"detail": str(exc)}, status=400)
        return None

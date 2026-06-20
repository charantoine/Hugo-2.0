"""JWT authentication with tenant context binding."""
from rest_framework_simplejwt.authentication import JWTAuthentication

from app_core.tenant_context import bind_tenant_context


class TenantAwareJWTAuthentication(JWTAuthentication):
    """Authenticate JWT and bind PostgreSQL tenant context before ORM queries."""

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        user, validated_token = result
        bind_tenant_context(request, user=user)
        return user, validated_token

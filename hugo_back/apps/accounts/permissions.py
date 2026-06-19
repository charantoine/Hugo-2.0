"""Permissions: ORGADMIN can manage own org, SUPERADMIN can manage all."""
from rest_framework import permissions

from .models import Role


class IsOrgAdminOrSuperadmin(permissions.BasePermission):
    """Allow ORGADMIN (for own org) and SUPERADMIN."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in (Role.ORGADMIN, Role.SUPERADMIN)


class IsOrgAdminSuperadminOrTrainer(permissions.BasePermission):
    """ORGADMIN, SUPERADMIN, TRAINER — gestion bibliothèque (création, indexation, liaison, désactivation)."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in (Role.ORGADMIN, Role.SUPERADMIN, Role.TRAINER)

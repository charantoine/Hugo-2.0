"""Permissions: ORGADMIN scoped to own org, SUPERADMIN multi-org."""
from rest_framework import permissions

from .models import Role


class IsSuperadmin(permissions.BasePermission):
    """Allow SUPERADMIN role only."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == Role.SUPERADMIN


class IsOrgAdmin(permissions.BasePermission):
    """Allow ORGADMIN role only."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == Role.ORGADMIN


class IsOrgAdminOrSuperadmin(permissions.BasePermission):
    """Allow ORGADMIN (org-scoped) and SUPERADMIN (multi-org via tenant context)."""

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

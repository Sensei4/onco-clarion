"""Permissions for FHIR export endpoints."""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Allow access only to users with role='admin' or superusers."""

    message = "You must be an admin to export FHIR data."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return getattr(user, "role", None) == "admin"

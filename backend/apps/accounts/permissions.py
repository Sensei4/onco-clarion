from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allow access only to users with role='admin' or Django superusers."""

    message = "You must be an admin to perform this action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return getattr(user, "role", None) == "admin"

from django.db.models import Q, QuerySet
from rest_framework import mixins, viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated

from .models import AuditEvent
from .serializers import AuditEventSerializer


class IsAdmin(BasePermission):
    """Allow access only to users with role='admin' or superusers."""

    message = "You must be an admin to view audit events."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return getattr(user, "role", None) == "admin"


class AuditEventViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Read-only access to audit events.

    Only admins can access. Regular admins see only their own
    organization; superusers see everything.
    """

    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AuditEventSerializer

    def get_queryset(self) -> QuerySet[AuditEvent]:
        user = self.request.user
        qs = AuditEvent.objects.select_related("user", "organization").order_by("-timestamp")

        if not user.is_superuser:
            if user.organization_id is None:
                return qs.none()
            qs = qs.filter(organization_id=user.organization_id)

        # Filters
        action = self.request.query_params.get("action")
        if action:
            qs = qs.filter(action=action)

        entity_type = self.request.query_params.get("entity_type")
        if entity_type:
            qs = qs.filter(entity_type=entity_type)

        entity_id = self.request.query_params.get("entity_id")
        if entity_id:
            qs = qs.filter(entity_id=entity_id)

        user_id = self.request.query_params.get("user")
        if user_id:
            qs = qs.filter(user_id=user_id)

        date_from = self.request.query_params.get("date_from")
        if date_from:
            qs = qs.filter(timestamp__gte=date_from)

        date_to = self.request.query_params.get("date_to")
        if date_to:
            qs = qs.filter(timestamp__lte=date_to)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(entity_repr__icontains=search)
                | Q(user__username__icontains=search)
                | Q(ip_address__icontains=search)
            )

        return qs

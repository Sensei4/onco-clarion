"""Read-only views for diagnostic reference data."""

from django.db.models import QuerySet
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import DiagnosticDepartment, DiagnosticMethod
from .serializers_diagnostics import (
    DiagnosticDepartmentSerializer,
    DiagnosticMethodSerializer,
)


class DiagnosticDepartmentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Read-only access to diagnostic departments of the current user's org."""

    permission_classes = [IsAuthenticated]
    serializer_class = DiagnosticDepartmentSerializer

    def get_queryset(self) -> QuerySet[DiagnosticDepartment]:
        user = self.request.user
        qs = DiagnosticDepartment.objects.prefetch_related("methods").order_by("name")

        # Multi-tenancy
        if not user.is_superuser:
            if user.organization_id is None:
                return qs.none()
            qs = qs.filter(organization_id=user.organization_id)

        # Filters
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)

        # By default show only active
        is_active = self.request.query_params.get("is_active")
        if is_active is None or is_active.lower() == "true":
            qs = qs.filter(is_active=True)

        return qs


class DiagnosticMethodViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Read-only access to diagnostic methods of the current user's org."""

    permission_classes = [IsAuthenticated]
    serializer_class = DiagnosticMethodSerializer

    def get_queryset(self) -> QuerySet[DiagnosticMethod]:
        user = self.request.user
        qs = DiagnosticMethod.objects.select_related("department").order_by("name")

        # Multi-tenancy via department.organization
        if not user.is_superuser:
            if user.organization_id is None:
                return qs.none()
            qs = qs.filter(department__organization_id=user.organization_id)

        # Filters
        department_id = self.request.query_params.get("department")
        if department_id:
            qs = qs.filter(department_id=department_id)

        # By default show only active
        is_active = self.request.query_params.get("is_active")
        if is_active is None or is_active.lower() == "true":
            qs = qs.filter(is_active=True)

        return qs

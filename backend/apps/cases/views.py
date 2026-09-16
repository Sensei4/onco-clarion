# Create your views here.
from django.db.models import Q, QuerySet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import CancerCase
from .serializers import (
    CancerCaseDetailSerializer,
    CancerCaseListSerializer,
)


class CancerCaseViewSet(viewsets.ModelViewSet):
    """CRUD for cancer cases, scoped to the current user's organization."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[CancerCase]:
        user = self.request.user
        queryset = CancerCase.objects.select_related("patient", "organization").order_by(
            "-created_at"
        )

        if user.is_superuser:
            return queryset

        if user.organization_id is None:
            return queryset.none()

        return queryset.filter(organization_id=user.organization_id)

    def get_serializer_class(self):
        if self.action == "list":
            return CancerCaseListSerializer
        return CancerCaseDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def filter_queryset(self, queryset: QuerySet[CancerCase]) -> QuerySet[CancerCase]:
        queryset = super().filter_queryset(queryset)

        # Filter by patient
        patient_id = self.request.query_params.get("patient")
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        # Filter by status
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Search by diagnosis code or text
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(diagnosis_code__icontains=search)
                | Q(diagnosis_text__icontains=search)
                | Q(patient__full_name__icontains=search)
            )

        return queryset

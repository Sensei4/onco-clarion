# Create your views here.
from django.db.models import Q, QuerySet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Patient
from .serializers import PatientDetailSerializer, PatientListSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """CRUD for patients, scoped to the current user's organization.

    - Listing supports search by full_name and medical_record_number.
    - Ordering is by full_name by default.
    - All authenticated users can read/write patients within their
      organization.
    - Superusers can read/write patients across all organizations.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Patient]:
        user = self.request.user
        queryset = Patient.objects.select_related("organization").order_by("full_name")

        if user.is_superuser:
            return queryset

        if user.organization_id is None:
            return queryset.none()

        return queryset.filter(organization_id=user.organization_id)

    def get_serializer_class(self):
        if self.action == "list":
            return PatientListSerializer
        return PatientDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def filter_queryset(self, queryset: QuerySet[Patient]) -> QuerySet[Patient]:
        queryset = super().filter_queryset(queryset)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) | Q(medical_record_number__icontains=search)
            )

        return queryset

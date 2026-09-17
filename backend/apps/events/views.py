from django.db.models import Q, QuerySet
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import (
    Event,
    EventConsilium,
    EventFollowupVisit,
    EventHospitalization,
    EventObservationVisit,
    EventPrimaryVisit,
    EventTreatment,
)
from .serializers import (
    EventConsiliumWriteSerializer,
    EventDetailSerializer,
    EventFollowupVisitWriteSerializer,
    EventHospitalizationWriteSerializer,
    EventListSerializer,
    EventObservationVisitWriteSerializer,
    EventPrimaryVisitWriteSerializer,
    EventTreatmentWriteSerializer,
)


class BaseEventReadViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Read-only base with multi-tenancy and event filters.

    Used by EventViewSet. Cannot create, update, or delete.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Event]:
        user = self.request.user
        qs = self.queryset.select_related(
            "case",
            "patient",
            "organization",
            "author",
        )

        if not user.is_superuser:
            if user.organization_id is None:
                return qs.none()
            qs = qs.filter(organization_id=user.organization_id)

        case_id = self.request.query_params.get("case")
        if case_id:
            qs = qs.filter(case_id=case_id)

        patient_id = self.request.query_params.get("patient")
        if patient_id:
            qs = qs.filter(patient_id=patient_id)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        type_filter = self.request.query_params.get("type")
        if type_filter:
            qs = qs.filter(type=type_filter)

        scheduled_from = self.request.query_params.get("scheduled_from")
        if scheduled_from:
            qs = qs.filter(scheduled_at__gte=scheduled_from)

        scheduled_to = self.request.query_params.get("scheduled_to")
        if scheduled_to:
            qs = qs.filter(scheduled_at__lte=scheduled_to)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(patient__full_name__icontains=search)
                | Q(patient__medical_record_number__icontains=search)
                | Q(notes__icontains=search)
            )

        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class EventViewSet(BaseEventReadViewSet):
    """Read-only list and retrieve for all events.

    Creation is handled by per-subtype viewsets below.
    POST/PUT/PATCH/DELETE are not allowed on this endpoint.
    """

    queryset = Event.objects.all().order_by("-scheduled_at")

    def get_serializer_class(self):
        if self.action == "list":
            return EventListSerializer
        return EventDetailSerializer


class BaseEventWriteViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Base for subtype-specific viewsets.

    Supports create, retrieve, update, delete — but not list.
    Listing is done via EventViewSet with ?type=... filter.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset.select_related(
            "case",
            "patient",
            "organization",
            "author",
        )
        if not user.is_superuser:
            if user.organization_id is None:
                return qs.none()
            qs = qs.filter(organization_id=user.organization_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class EventPrimaryVisitViewSet(BaseEventWriteViewSet):
    queryset = EventPrimaryVisit.objects.all().order_by("-scheduled_at")
    serializer_class = EventPrimaryVisitWriteSerializer


class EventFollowupVisitViewSet(BaseEventWriteViewSet):
    queryset = EventFollowupVisit.objects.all().order_by("-scheduled_at")
    serializer_class = EventFollowupVisitWriteSerializer


class EventObservationVisitViewSet(BaseEventWriteViewSet):
    queryset = EventObservationVisit.objects.all().order_by("-scheduled_at")
    serializer_class = EventObservationVisitWriteSerializer


class EventConsiliumViewSet(BaseEventWriteViewSet):
    queryset = EventConsilium.objects.all().order_by("-scheduled_at")
    serializer_class = EventConsiliumWriteSerializer


class EventHospitalizationViewSet(BaseEventWriteViewSet):
    queryset = EventHospitalization.objects.all().order_by("-scheduled_at")
    serializer_class = EventHospitalizationWriteSerializer


class EventTreatmentViewSet(BaseEventWriteViewSet):
    queryset = EventTreatment.objects.all().order_by("-scheduled_at")
    serializer_class = EventTreatmentWriteSerializer

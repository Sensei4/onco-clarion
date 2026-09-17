from django.db.models import Q, QuerySet
from django_fsm import TransitionNotAllowed
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CancerCase
from .serializers import (
    CancerCaseDetailSerializer,
    CancerCaseListSerializer,
    StatusTransitionSerializer,
    TransitionActionSerializer,
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

        patient_id = self.request.query_params.get("patient")
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(diagnosis_code__icontains=search)
                | Q(diagnosis_text__icontains=search)
                | Q(patient__full_name__icontains=search)
            )

        return queryset

    @action(
        detail=True,
        methods=["post"],
        url_path="transition",
        url_name="transition",
    )
    def transition_action(self, request, pk=None):
        """Apply a state machine transition to a case."""
        case = self.get_object()
        serializer = TransitionActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_name = serializer.validated_data["action"]
        reason = serializer.validated_data.get("reason", "")

        method = getattr(case, action_name)
        try:
            method(by_user=request.user, reason=reason)
        except TransitionNotAllowed as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_409_CONFLICT,
            )

        case.save()
        return Response(CancerCaseDetailSerializer(case).data)

    @action(
        detail=True,
        methods=["get"],
        url_path="transitions",
        url_name="transitions",
    )
    def transitions_list(self, request, pk=None):
        """Return the audit trail for a case."""
        case = self.get_object()
        transitions = case.status_transitions.select_related("transitioned_by").all()
        serializer = StatusTransitionSerializer(transitions, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="waiting-list",
        url_name="waiting-list",
    )
    def waiting_list(self, request):
        """Return cases currently waiting for hospitalization.

        Each case includes the date it entered the waiting list
        (from the latest StatusTransition) and days waiting.
        """
        from django.db.models import OuterRef, Subquery
        from django.utils import timezone

        from .models import StatusTransition

        # Subquery: latest transition INTO waiting_hospitalization for each case
        latest_waiting = (
            StatusTransition.objects.filter(
                case=OuterRef("pk"),
                to_status="waiting_hospitalization",
            )
            .order_by("-transitioned_at")
            .values("transitioned_at")[:1]
        )

        qs = (
            self.get_queryset()
            .filter(status="waiting_hospitalization")
            .annotate(waiting_since=Subquery(latest_waiting))
            .order_by("waiting_since")
        )

        now = timezone.now()
        results = []
        for case in qs:
            waiting_days = None
            if case.waiting_since:
                waiting_days = (now - case.waiting_since).days
            item = CancerCaseDetailSerializer(case, context={"request": request}).data
            item["waiting_since"] = case.waiting_since
            item["waiting_days"] = waiting_days
            results.append(item)

        return Response(results)

    @action(
        detail=False,
        methods=["get"],
        url_path="observation-list",
        url_name="observation-list",
    )
    def observation_list(self, request):
        """Return cases currently under observation.

        Each case includes the date of the last completed
        observation visit and the next planned one (if any).
        """
        from django.db.models import OuterRef, Subquery

        from apps.events.models import Event

        last_visit = (
            Event.objects.filter(
                case=OuterRef("pk"),
                type="observation_visit",
                status="done",
            )
            .order_by("-scheduled_at")
            .values("scheduled_at")[:1]
        )

        next_visit = (
            Event.objects.filter(
                case=OuterRef("pk"),
                type="observation_visit",
                status="planned",
            )
            .order_by("scheduled_at")
            .values("scheduled_at")[:1]
        )

        qs = (
            self.get_queryset()
            .filter(status="observation")
            .annotate(
                last_visit_at=Subquery(last_visit),
                next_visit_at=Subquery(next_visit),
            )
            .order_by("-last_visit_at", "patient__full_name")
        )

        results = []
        for case in qs:
            item = CancerCaseDetailSerializer(case, context={"request": request}).data
            item["last_visit_at"] = case.last_visit_at
            item["next_visit_at"] = case.next_visit_at
            results.append(item)

        return Response(results)

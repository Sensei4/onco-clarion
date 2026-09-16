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

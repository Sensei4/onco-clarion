from django.db.models import Q, QuerySet
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.audit.mixins import AuditLogMixin, log_custom_action
from apps.audit.models import AuditEvent

from .models import Referral
from .serializers import (
    CancelReferralSerializer,
    CompleteReferralSerializer,
    ReferralDetailSerializer,
    ReferralListSerializer,
)


class ReferralViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """CRUD for referrals, scoped to the current user's organization.

    Custom actions:
      - POST /api/referrals/{id}/complete/   (with optional result_text)
      - POST /api/referrals/{id}/cancel/     (with optional reason)
      - POST /api/referrals/{id}/reopen/
    """

    audit_entity_type = "Referral"
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Referral]:
        user = self.request.user
        qs = Referral.objects.select_related(
            "case",
            "case__patient",
            "event",
            "organization",
            "ordered_by",
            "completed_by",
        ).order_by("-ordered_at")

        if not user.is_superuser:
            if user.organization_id is None:
                return qs.none()
            qs = qs.filter(organization_id=user.organization_id)

        case_id = self.request.query_params.get("case")
        if case_id:
            qs = qs.filter(case_id=case_id)

        event_id = self.request.query_params.get("event")
        if event_id:
            qs = qs.filter(event_id=event_id)

        type_filter = self.request.query_params.get("type")
        if type_filter:
            qs = qs.filter(type=type_filter)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(notes__icontains=search)
                | Q(result_text__icontains=search)
                | Q(case__patient__full_name__icontains=search)
                | Q(case__patient__medical_record_number__icontains=search)
            )

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ReferralListSerializer
        if self.action == "complete":
            return CompleteReferralSerializer
        if self.action == "cancel":
            return CancelReferralSerializer
        return ReferralDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(ordered_by=self.request.user)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark the referral as completed and record the result."""
        referral = self.get_object()

        if referral.status != Referral.Status.ORDERED:
            return Response(
                {"detail": f"Cannot complete a referral in status '{referral.status}'."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = CompleteReferralSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        referral.status = Referral.Status.COMPLETED
        referral.result_text = serializer.validated_data.get("result_text", "")
        referral.result_received_at = timezone.now()
        referral.completed_by = request.user
        referral.save()

        log_custom_action(request, referral, AuditEvent.Action.UPDATE)

        return Response(ReferralDetailSerializer(referral, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel the referral."""
        referral = self.get_object()

        if referral.status != Referral.Status.ORDERED:
            return Response(
                {"detail": f"Cannot cancel a referral in status '{referral.status}'."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = CancelReferralSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reason = serializer.validated_data.get("reason", "")
        if reason:
            referral.notes = (
                referral.notes + "\n\n" if referral.notes else ""
            ) + f"Cancelled: {reason}"

        referral.status = Referral.Status.CANCELLED
        referral.save()

        log_custom_action(request, referral, AuditEvent.Action.UPDATE)

        return Response(ReferralDetailSerializer(referral, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        """Return a cancelled or completed referral back to 'ordered'."""
        referral = self.get_object()

        if referral.status == Referral.Status.ORDERED:
            return Response(
                {"detail": "Referral is already ordered."},
                status=status.HTTP_409_CONFLICT,
            )

        referral.status = Referral.Status.ORDERED
        referral.result_text = ""
        referral.result_received_at = None
        referral.completed_by = None
        referral.save()

        log_custom_action(request, referral, AuditEvent.Action.UPDATE)

        return Response(ReferralDetailSerializer(referral, context={"request": request}).data)

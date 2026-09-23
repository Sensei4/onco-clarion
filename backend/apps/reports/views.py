from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.cases.models import CancerCase, StatusTransition
from apps.events.models import Event


def parse_date_range(request):
    """Parse date_from / date_to query params into a Q filter for datetime fields.

    Returns a tuple (q_filter, date_from, date_to).
    """
    date_from = request.query_params.get("date_from")
    date_to = request.query_params.get("date_to")

    q = Q()
    if date_from:
        q &= Q(created_at__gte=date_from)
    if date_to:
        q &= Q(created_at__lte=date_to)
    return q, date_from, date_to


def organization_filter(user):
    """Return a Q object to scope reports to the user's organization."""
    if user.is_superuser:
        return Q()
    if user.organization_id is None:
        return Q(pk__in=[])
    return Q(organization_id=user.organization_id)


class ReportViewSet(viewsets.ViewSet):
    """Read-only reports, scoped to the current user's organization."""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="cases-by-status")
    def cases_by_status(self, request):
        """Count cases grouped by their current status."""
        org_filter = organization_filter(request.user)
        date_filter, _, _ = parse_date_range(request)

        qs = (
            CancerCase.objects.filter(org_filter)
            .filter(date_filter)
            .values("status")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Ensure all statuses are present, even with zero
        all_statuses = [s.value for s in CancerCase.Status]
        counts = {s: 0 for s in all_statuses}
        for row in qs:
            counts[row["status"]] = row["count"]

        results = [
            {"status": status, "label": CancerCase.Status(status).label, "count": counts[status]}
            for status in all_statuses
        ]
        return Response({"total": sum(counts.values()), "results": results})

    @action(detail=False, methods=["get"], url_path="cases-by-stage")
    def cases_by_stage(self, request):
        """Count cases grouped by clinical stage."""
        org_filter = organization_filter(request.user)
        date_filter, _, _ = parse_date_range(request)

        qs = (
            CancerCase.objects.filter(org_filter)
            .filter(date_filter)
            .values("stage")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Normalize "IIIA" → "III", "IIB" → "II", etc.
        known = ["I", "II", "III", "IV"]
        counts = {s: 0 for s in known}
        unknown_count = 0

        for row in qs:
            stage = (row["stage"] or "").strip().upper()
            matched = None
            # Check longest prefixes first (IV before I)
            for prefix in ["IV", "III", "II", "I"]:
                if stage.startswith(prefix):
                    matched = prefix
                    break
            if matched:
                counts[matched] += row["count"]
            else:
                unknown_count += row["count"]

        results = [
            {"stage": stage, "count": counts.get(stage, 0)} for stage in ["I", "II", "III", "IV"]
        ]
        results.append({"stage": "unknown", "count": unknown_count})

        return Response({"total": sum(r["count"] for r in results), "results": results})

    @action(detail=False, methods=["get"], url_path="waiting-time")
    def waiting_time(self, request):
        """Waiting time for cases currently in waiting_hospitalization.

        For each case, finds the latest transition INTO waiting_hospitalization
        and computes days since then. Returns average, median, max, and top-10.
        """
        from django.db.models import OuterRef, Subquery

        org_filter = organization_filter(request.user)

        latest_waiting = (
            StatusTransition.objects.filter(
                case=OuterRef("pk"),
                to_status="waiting_hospitalization",
            )
            .order_by("-transitioned_at")
            .values("transitioned_at")[:1]
        )

        qs = CancerCase.objects.filter(org_filter, status="waiting_hospitalization").annotate(
            waiting_since=Subquery(latest_waiting)
        )

        now = timezone.now()
        items = []
        for case in qs:
            if not case.waiting_since:
                continue
            days = (now - case.waiting_since).days
            items.append(
                {
                    "case_id": case.id,
                    "patient_name": case.patient.full_name,
                    "patient_mrn": case.patient.medical_record_number,
                    "diagnosis_code": case.diagnosis_code,
                    "stage": case.stage,
                    "waiting_since": case.waiting_since,
                    "waiting_days": days,
                }
            )

        items.sort(key=lambda x: x["waiting_days"], reverse=True)

        days_list = [i["waiting_days"] for i in items]
        avg_days = round(sum(days_list) / len(days_list), 1) if days_list else 0
        max_days = max(days_list) if days_list else 0

        # Median
        median_days = 0
        if days_list:
            sorted_days = sorted(days_list)
            n = len(sorted_days)
            if n % 2 == 0:
                median_days = (sorted_days[n // 2 - 1] + sorted_days[n // 2]) / 2
            else:
                median_days = sorted_days[n // 2]

        return Response(
            {
                "total": len(items),
                "avg_days": avg_days,
                "median_days": median_days,
                "max_days": max_days,
                "top": items[:10],
            }
        )

    @action(detail=False, methods=["get"], url_path="events-by-type")
    def events_by_type(self, request):
        """Count events grouped by type."""
        org_filter = organization_filter(request.user).copy()
        org_filter &= (
            Q(organization_id=request.user.organization_id)
            if not request.user.is_superuser
            else Q()
        )

        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        qs = Event.objects.all()
        if not request.user.is_superuser:
            if request.user.organization_id is None:
                return Response({"total": 0, "results": []})
            qs = qs.filter(organization_id=request.user.organization_id)

        if date_from:
            qs = qs.filter(scheduled_at__gte=date_from)
        if date_to:
            qs = qs.filter(scheduled_at__lte=date_to)

        qs = qs.values("type").annotate(count=Count("id")).order_by("-count")

        all_types = [t.value for t in Event.Type]
        counts = {t: 0 for t in all_types}
        for row in qs:
            counts[row["type"]] = row["count"]

        results = [{"type": t, "label": Event.Type(t).label, "count": counts[t]} for t in all_types]
        return Response({"total": sum(counts.values()), "results": results})

    @action(detail=False, methods=["get"], url_path="top-diagnoses")
    def top_diagnoses(self, request):
        """Top-10 most frequent diagnosis codes (ICD-O-3)."""
        org_filter = organization_filter(request.user)
        date_filter, _, _ = parse_date_range(request)

        qs = (
            CancerCase.objects.filter(org_filter)
            .filter(date_filter)
            .exclude(diagnosis_code="")
            .values("diagnosis_code")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        return Response(
            {
                "results": [
                    {"diagnosis_code": row["diagnosis_code"], "count": row["count"]} for row in qs
                ]
            }
        )

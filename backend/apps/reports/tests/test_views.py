import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestCasesByStatus:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/reports/cases-by-status/")
        assert response.status_code == 403

    def test_returns_all_statuses(self, api_client, doctor, case_ii, case_iii):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/reports/cases-by-status/")
        assert response.status_code == 200
        data = response.json()
        # 9 statuses always present
        assert len(data["results"]) == 9
        assert data["total"] == 2

    def test_counts_by_status(self, api_client, doctor, case_ii, case_iii):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/reports/cases-by-status/")
        results = {r["status"]: r["count"] for r in response.json()["results"]}
        assert results["observation"] == 1
        assert results["diagnostic"] == 1
        assert results["new"] == 0

    def test_multi_tenancy(self, api_client, doctor, case_ii, other_case):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/reports/cases-by-status/")
        # Doctor sees only Org A (1 case), not Org B
        assert response.json()["total"] == 1

    def test_superuser_sees_all(self, api_client, superuser, case_ii, other_case):
        api_client.force_authenticate(user=superuser)
        response = api_client.get("/api/reports/cases-by-status/")
        assert response.json()["total"] == 2


@pytest.mark.django_db
class TestCasesByStage:
    def test_normalizes_stage_prefix(self, api_client, doctor, case_ii, case_iii):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/reports/cases-by-stage/")
        data = response.json()
        assert data["total"] == 2
        counts = {r["stage"]: r["count"] for r in data["results"]}
        assert counts["II"] == 1  # IIB → II
        assert counts["III"] == 1  # IIIA → III
        assert counts["unknown"] == 0

    def test_empty_stage_counted_as_unknown(self, api_client, doctor, patient, organization):
        from apps.cases.models import CancerCase

        CancerCase.objects.create(
            patient=patient,
            organization=organization,
            diagnosis_code="X",
            stage="",
        )
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/reports/cases-by-stage/")
        counts = {r["stage"]: r["count"] for r in response.json()["results"]}
        assert counts["unknown"] == 1


@pytest.mark.django_db
class TestEventsByType:
    def test_counts_events(self, api_client, doctor, event):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/reports/events-by-type/")
        data = response.json()
        assert data["total"] == 1
        counts = {r["type"]: r["count"] for r in data["results"]}
        assert counts["primary_visit"] == 1

    def test_multi_tenancy(self, api_client, doctor, event, other_case):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/reports/events-by-type/")
        assert response.json()["total"] == 1


@pytest.mark.django_db
class TestTopDiagnoses:
    def test_returns_top_diagnoses(self, api_client, doctor, case_ii, case_iii):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/reports/top-diagnoses/")
        results = response.json()["results"]
        codes = {r["diagnosis_code"] for r in results}
        assert "C50.9" in codes
        assert "C34.9" in codes

    def test_excludes_empty_diagnoses(self, api_client, doctor, patient, organization):
        from apps.cases.models import CancerCase

        CancerCase.objects.create(
            patient=patient,
            organization=organization,
            diagnosis_code="",
        )
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/reports/top-diagnoses/")
        results = response.json()["results"]
        assert all(r["diagnosis_code"] for r in results)


@pytest.mark.django_db
class TestWaitingTime:
    def test_empty_when_no_waiting_cases(self, api_client, doctor, case_ii):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/reports/waiting-time/")
        data = response.json()
        assert data["total"] == 0
        assert data["avg_days"] == 0
        assert data["top"] == []

    def test_computes_waiting_days(self, api_client, doctor, patient, organization):
        from django_fsm import TransitionNotAllowed  # noqa: F401

        from apps.cases.models import CancerCase, StatusTransition

        case = CancerCase.objects.create(
            patient=patient,
            organization=organization,
            diagnosis_code="X",
            status=CancerCase.Status.WAITING_HOSPITALIZATION,
        )
        # Manually create a transition to set waiting_since
        from django.utils import timezone

        StatusTransition.objects.create(
            case=case,
            from_status="consilium",
            to_status="waiting_hospitalization",
            transitioned_by=doctor,
            transitioned_at=timezone.now() - timezone.timedelta(days=5),
        )

        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/reports/waiting-time/")
        data = response.json()
        assert data["total"] == 1
        assert data["avg_days"] == 5
        assert data["top"][0]["waiting_days"] == 5

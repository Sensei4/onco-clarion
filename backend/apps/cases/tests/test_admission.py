import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestAdmissionQueue:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/cases/admission-queue/")
        assert response.status_code == 403

    def test_returns_waiting_cases(self, api_client, doctor, case_in_waiting):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/admission-queue/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == case_in_waiting.id

    def test_excludes_non_waiting_cases(self, api_client, doctor, case):
        """Case in 'new' status should not appear in admission queue."""
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/admission-queue/")
        assert response.status_code == 200
        assert response.json() == []

    def test_multi_tenancy(
        self,
        api_client,
        doctor,
        case_in_waiting,
        other_case_in_waiting,
    ):
        """Doctor sees only cases from their own organization."""
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/admission-queue/")
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == case_in_waiting.id

    def test_superuser_sees_all(
        self,
        api_client,
        superuser,
        case_in_waiting,
        other_case_in_waiting,
    ):
        api_client.force_authenticate(user=superuser)
        response = api_client.get("/api/cases/admission-queue/")
        assert len(response.json()) == 2


@pytest.mark.django_db
class TestAdmissionQueueFields:
    def test_includes_patient_fields(self, api_client, doctor, case_in_waiting):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/admission-queue/")
        item = response.json()[0]
        assert item["patient_name"] == "Ivan Petrov"
        assert item["patient_mrn"] == "MRN-0001"
        assert item["patient_birth_date"] == "1965-03-15"
        assert item["patient_age"] is not None
        assert item["patient_sex"] == "male"
        assert "patient_insurance_policy_number" in item

    def test_includes_waiting_context(self, api_client, doctor, case_in_waiting):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/admission-queue/")
        item = response.json()[0]
        assert item["waiting_since"] is not None
        assert item["waiting_days"] is not None
        assert item["waiting_days"] >= 0

    def test_consilium_fields_empty_without_consilium(self, api_client, doctor, case_in_waiting):
        """Without a done consilium, fields are empty."""
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/admission-queue/")
        item = response.json()[0]
        assert item["last_consilium_date"] is None
        assert item["last_consilium_decision"] == ""
        assert item["last_consilium_recommended_plan"] == ""


@pytest.mark.django_db
class TestAdmissionQueueSorting:
    def test_longest_waiting_first(self, api_client, doctor, organization, patient):
        """Cases are ordered by waiting_since ASC."""
        from django.utils import timezone

        from apps.cases.models import CancerCase, StatusTransition

        # Create two cases with different waiting_since
        c1 = CancerCase.objects.create(
            patient=patient,
            organization=organization,
            diagnosis_code="C50.9",
        )
        c1.start_diagnostics(by_user=doctor)
        c1.save()
        c1.schedule_consilium(by_user=doctor)
        c1.save()
        c1.approve_hospitalization(by_user=doctor)
        c1.save()

        c2 = CancerCase.objects.create(
            patient=patient,
            organization=organization,
            diagnosis_code="C51.9",
        )
        c2.start_diagnostics(by_user=doctor)
        c2.save()
        c2.schedule_consilium(by_user=doctor)
        c2.save()
        c2.approve_hospitalization(by_user=doctor)
        c2.save()

        # Manually set waiting_since: c1 older than c2
        now = timezone.now()
        StatusTransition.objects.filter(case=c1, to_status="waiting_hospitalization").update(
            transitioned_at=now - timezone.timedelta(days=5)
        )
        StatusTransition.objects.filter(case=c2, to_status="waiting_hospitalization").update(
            transitioned_at=now - timezone.timedelta(days=1)
        )

        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/admission-queue/")
        data = response.json()
        assert len(data) == 2
        # c1 should be first because it waited 5 days vs 1 day
        assert data[0]["id"] == c1.id
        assert data[0]["waiting_days"] >= 5
        assert data[1]["id"] == c2.id
        assert data[1]["waiting_days"] >= 1

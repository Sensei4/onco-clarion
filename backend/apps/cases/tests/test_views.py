import pytest
from rest_framework.test import APIClient

from apps.cases.models import CancerCase


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestCaseList:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/cases/")
        assert response.status_code == 403

    def test_doctor_sees_only_own_organization_cases(self, api_client, doctor, case, other_case):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["diagnosis_code"] == "C50.9"

    def test_superuser_sees_all_cases(self, api_client, superuser, case, other_case):
        api_client.force_authenticate(user=superuser)
        response = api_client.get("/api/cases/")
        assert response.json()["count"] == 2


@pytest.mark.django_db
class TestCaseFilters:
    def test_filter_by_patient(self, api_client, doctor, case):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/cases/?patient={case.patient.id}")
        assert response.json()["count"] == 1

    def test_filter_by_status(self, api_client, doctor, case):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/?status=new")
        assert response.json()["count"] == 1

    def test_filter_by_unknown_status_returns_empty(self, api_client, doctor, case):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/?status=remission")
        assert response.json()["count"] == 0

    def test_search_by_diagnosis_code(self, api_client, doctor, case):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/?search=C50")
        assert response.json()["count"] == 1

    def test_search_by_patient_name(self, api_client, doctor, case):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/?search=Ivan")
        assert response.json()["count"] == 1

    def test_search_no_match(self, api_client, doctor, case):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/cases/?search=ZZZ")
        assert response.json()["count"] == 0


@pytest.mark.django_db
class TestCaseRetrieve:
    def test_doctor_can_retrieve_own_case(self, api_client, doctor, case):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/cases/{case.id}/")
        assert response.status_code == 200
        assert response.json()["diagnosis_code"] == "C50.9"
        assert response.json()["status"] == "new"

    def test_doctor_cannot_retrieve_foreign_case(self, api_client, doctor, other_case):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/cases/{other_case.id}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestCaseCreate:
    def test_doctor_can_create_in_own_organization(self, api_client, doctor, organization, patient):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/cases/",
            {
                "patient": patient.id,
                "organization": organization.id,
                "diagnosis_code": "C34.9",
                "diagnosis_text": "Lung cancer",
                "stage": "IIIA",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["status"] == "new"

    def test_status_sent_by_client_is_ignored(self, api_client, doctor, organization, patient):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/cases/",
            {
                "patient": patient.id,
                "organization": organization.id,
                "diagnosis_code": "C34.9",
                "status": "remission",  # should be ignored
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["status"] == "new"

    def test_doctor_cannot_create_in_foreign_organization(
        self, api_client, doctor, other_organization, patient
    ):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/cases/",
            {
                "patient": patient.id,
                "organization": other_organization.id,
                "diagnosis_code": "C34.9",
            },
            format="json",
        )
        assert response.status_code == 400
        assert "organization" in response.json()

    def test_patient_and_organization_must_match(
        self, api_client, doctor, organization, other_patient
    ):
        """Case organization must match patient organization."""
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/cases/",
            {
                "patient": other_patient.id,  # patient from other org
                "organization": organization.id,  # doctor's org
                "diagnosis_code": "C34.9",
            },
            format="json",
        )
        assert response.status_code == 400
        assert "patient" in response.json()


@pytest.mark.django_db
class TestCaseUpdate:
    def test_doctor_can_update_diagnosis(self, api_client, doctor, case):
        api_client.force_authenticate(user=doctor)
        response = api_client.patch(
            f"/api/cases/{case.id}/",
            {"diagnosis_text": "Updated"},
            format="json",
        )
        assert response.status_code == 200
        case.refresh_from_db(fields=["diagnosis_text"])
        assert case.diagnosis_text == "Updated"

    def test_status_cannot_be_changed_via_patch(self, api_client, doctor, case):
        api_client.force_authenticate(user=doctor)
        response = api_client.patch(
            f"/api/cases/{case.id}/",
            {"status": "remission"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["status"] == "new"
        fresh = CancerCase.objects.get(pk=case.pk)
        assert fresh.status == "new"
        assert case.status == "new"

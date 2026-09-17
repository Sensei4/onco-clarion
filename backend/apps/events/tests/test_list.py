import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestEventList:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/events/")
        assert response.status_code == 403

    def test_doctor_sees_only_own_organization_events(
        self, api_client, doctor, primary_visit, other_primary_visit
    ):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/events/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["patient_name"] == "Ivan Petrov"

    def test_superuser_sees_all_events(
        self, api_client, superuser, primary_visit, other_primary_visit
    ):
        api_client.force_authenticate(user=superuser)
        response = api_client.get("/api/events/")
        assert response.json()["count"] == 2

    def test_list_returns_denormalized_fields(self, api_client, doctor, primary_visit):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/events/")
        item = response.json()["results"][0]
        assert item["patient_name"] == "Ivan Petrov"
        assert item["patient_mrn"] == "MRN-0001"
        assert item["case_diagnosis"] == "C50.9"
        assert item["author_name"] == "doctor"
        assert item["type"] == "primary_visit"


@pytest.mark.django_db
class TestEventFilters:
    def test_filter_by_case(
        self, api_client, doctor, case, primary_visit, consilium, other_primary_visit
    ):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/events/?case={case.id}")
        # doctor only sees own org, so other_primary_visit is excluded
        assert response.json()["count"] == 2

    def test_filter_by_patient(self, api_client, doctor, patient, primary_visit, consilium):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/events/?patient={patient.id}")
        assert response.json()["count"] == 2

    def test_filter_by_type(self, api_client, doctor, primary_visit, consilium, treatment):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/events/?type=consilium")
        assert response.json()["count"] == 1
        assert response.json()["results"][0]["type"] == "consilium"

    def test_filter_by_status(self, api_client, doctor, primary_visit, consilium, treatment):
        api_client.force_authenticate(user=doctor)
        # primary_visit и consilium — done, treatment — planned
        response = api_client.get("/api/events/?status=planned")
        assert response.json()["count"] == 1
        assert response.json()["results"][0]["type"] == "treatment"

    def test_search_by_patient_name(self, api_client, doctor, primary_visit, other_primary_visit):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/events/?search=Ivan")
        # doctor sees only his org (Ivan), superuser would see both
        assert response.json()["count"] == 1

    def test_search_no_match(self, api_client, doctor, primary_visit):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/events/?search=ZZZZ")
        assert response.json()["count"] == 0

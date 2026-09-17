import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestEventDetail:
    def test_primary_visit_details(self, api_client, doctor, primary_visit):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/events/{primary_visit.id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "primary_visit"
        assert data["details"]["chief_complaint"] == "Pain"

    def test_consilium_details(self, api_client, doctor, consilium):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/events/{consilium.id}/")
        data = response.json()
        assert data["type"] == "consilium"
        assert data["details"]["decision"] == "Chemotherapy recommended"
        assert "doctor" in data["details"]["participant_names"]

    def test_treatment_details(self, api_client, doctor, treatment):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/events/{treatment.id}/")
        data = response.json()
        assert data["type"] == "treatment"
        assert data["details"]["modality"] == "chemo"
        assert data["details"]["regimen"] == "AC"
        assert data["details"]["cycle_number"] == 1
        assert data["details"]["cycle_total"] == 4

    def test_doctor_cannot_get_foreign_event(self, api_client, doctor, other_primary_visit):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/events/{other_primary_visit.id}/")
        assert response.status_code == 404

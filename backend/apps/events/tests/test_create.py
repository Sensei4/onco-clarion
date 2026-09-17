import pytest
from rest_framework.test import APIClient

from apps.events.models import (
    Event,
    EventConsilium,
    EventFollowupVisit,
    EventHospitalization,
    EventObservationVisit,
    EventPrimaryVisit,
    EventTreatment,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestEventCreate:
    def test_create_primary_visit(self, api_client, doctor, case, patient, organization):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/events/primary-visits/",
            {
                "case": case.id,
                "patient": patient.id,
                "organization": organization.id,
                "status": "planned",
                "scheduled_at": "2026-10-01T10:00:00Z",
                "chief_complaint": "Chest pain",
            },
            format="json",
        )
        assert response.status_code == 201
        event = EventPrimaryVisit.objects.get(id=response.json()["id"])
        assert event.type == Event.Type.PRIMARY_VISIT
        assert event.author == doctor
        assert event.chief_complaint == "Chest pain"

    def test_create_followup_visit(self, api_client, doctor, case, patient, organization):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/events/followup-visits/",
            {
                "case": case.id,
                "patient": patient.id,
                "organization": organization.id,
                "status": "planned",
                "scheduled_at": "2026-10-05T10:00:00Z",
                "findings": "Stable",
                "plan": "Continue",
            },
            format="json",
        )
        assert response.status_code == 201
        assert EventFollowupVisit.objects.filter(id=response.json()["id"]).exists()

    def test_create_observation_visit(self, api_client, doctor, case, patient, organization):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/events/observation-visits/",
            {
                "case": case.id,
                "patient": patient.id,
                "organization": organization.id,
                "status": "planned",
                "scheduled_at": "2026-10-10T10:00:00Z",
                "findings": "No change",
            },
            format="json",
        )
        assert response.status_code == 201
        assert EventObservationVisit.objects.filter(id=response.json()["id"]).exists()

    def test_create_consilium(self, api_client, doctor, case, patient, organization):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/events/consilia/",
            {
                "case": case.id,
                "patient": patient.id,
                "organization": organization.id,
                "status": "planned",
                "scheduled_at": "2026-10-15T10:00:00Z",
                "decision": "Chemo",
                "participants": [doctor.id],
            },
            format="json",
        )
        assert response.status_code == 201
        cons = EventConsilium.objects.get(id=response.json()["id"])
        assert doctor in cons.participants.all()

    def test_create_hospitalization(self, api_client, doctor, case, patient, organization):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/events/hospitalizations/",
            {
                "case": case.id,
                "patient": patient.id,
                "organization": organization.id,
                "status": "planned",
                "scheduled_at": "2026-10-20T10:00:00Z",
                "ward": "Ward 5",
                "reason": "Surgery",
            },
            format="json",
        )
        assert response.status_code == 201
        hosp = EventHospitalization.objects.get(id=response.json()["id"])
        assert hosp.ward == "Ward 5"

    def test_create_treatment(self, api_client, doctor, case, patient, organization):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/events/treatments/",
            {
                "case": case.id,
                "patient": patient.id,
                "organization": organization.id,
                "status": "planned",
                "scheduled_at": "2026-10-25T10:00:00Z",
                "modality": "chemo",
                "regimen": "FOLFOX",
                "cycle_number": 1,
                "cycle_total": 6,
            },
            format="json",
        )
        assert response.status_code == 201
        treat = EventTreatment.objects.get(id=response.json()["id"])
        assert treat.modality == "chemo"
        assert treat.regimen == "FOLFOX"

    def test_author_is_current_user_not_payload(
        self, api_client, doctor, superuser, case, patient, organization
    ):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/events/primary-visits/",
            {
                "case": case.id,
                "patient": patient.id,
                "organization": organization.id,
                "status": "planned",
                "scheduled_at": "2026-10-01T10:00:00Z",
                "author": superuser.id,  # should be ignored
            },
            format="json",
        )
        assert response.status_code == 201
        event = EventPrimaryVisit.objects.get(id=response.json()["id"])
        assert event.author == doctor

    def test_post_to_base_events_is_not_allowed(
        self, api_client, doctor, case, patient, organization
    ):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/events/",
            {
                "case": case.id,
                "patient": patient.id,
                "organization": organization.id,
                "type": "primary_visit",
                "scheduled_at": "2026-10-01T10:00:00Z",
            },
            format="json",
        )
        assert response.status_code == 405

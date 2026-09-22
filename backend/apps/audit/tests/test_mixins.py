import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organization
from apps.audit.models import AuditEvent
from apps.patients.models import Patient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def organization(db):
    return Organization.objects.create(name="Org", country="RU")


@pytest.fixture
def doctor(db, organization):
    return User.objects.create_user(
        username="doctor",
        password="strong-pass-12345",
        role="doctor",
        organization=organization,
    )


@pytest.fixture
def patient(db, organization):
    from datetime import date

    return Patient.objects.create(
        organization=organization,
        full_name="Ivan Petrov",
        birth_date=date(1965, 3, 15),
        sex="male",
        medical_record_number="MRN-0001",
    )


@pytest.mark.django_db
class TestAuditMixin:
    def test_retrieve_creates_view_audit(self, api_client, doctor, patient):
        api_client.force_authenticate(user=doctor)
        assert AuditEvent.objects.count() == 0

        api_client.get(f"/api/patients/{patient.id}/")

        events = AuditEvent.objects.filter(action="view")
        assert events.count() == 1
        event = events.first()
        assert event.entity_type == "Patient"
        assert event.entity_id == patient.id
        assert "Ivan Petrov" in event.entity_repr
        assert event.user == doctor

    def test_create_creates_create_audit(self, api_client, doctor, organization):
        api_client.force_authenticate(user=doctor)

        api_client.post(
            "/api/patients/",
            {
                "organization": organization.id,
                "full_name": "New Patient",
                "birth_date": "1990-01-01",
                "sex": "male",
                "medical_record_number": "MRN-NEW",
            },
            format="json",
        )

        events = AuditEvent.objects.filter(action="create")
        assert events.count() == 1
        assert events.first().entity_type == "Patient"

    def test_update_creates_update_audit(self, api_client, doctor, patient):
        api_client.force_authenticate(user=doctor)

        api_client.patch(
            f"/api/patients/{patient.id}/",
            {"full_name": "Updated Name"},
            format="json",
        )

        events = AuditEvent.objects.filter(action="update")
        assert events.count() == 1
        assert events.first().entity_id == patient.id

    def test_delete_creates_delete_audit(self, api_client, doctor, patient):
        api_client.force_authenticate(user=doctor)

        api_client.delete(f"/api/patients/{patient.id}/")

        events = AuditEvent.objects.filter(action="delete")
        assert events.count() == 1
        # entity_repr preserved even after deletion
        assert "Ivan Petrov" in events.first().entity_repr

    def test_list_does_not_create_audit(self, api_client, doctor, patient):
        api_client.force_authenticate(user=doctor)

        api_client.get("/api/patients/")

        assert AuditEvent.objects.count() == 0

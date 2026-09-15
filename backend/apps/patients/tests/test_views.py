from datetime import date

import pytest
from rest_framework.test import APIClient

from apps.patients.models import Patient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestPatientList:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/patients/")
        assert response.status_code == 403

    def test_doctor_sees_only_own_organization_patients(
        self, api_client, doctor, patient, other_patient
    ):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/patients/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["full_name"] == "Ivan Petrov"

    def test_other_doctor_sees_only_own_organization_patients(
        self, api_client, other_doctor, patient, other_patient
    ):
        api_client.force_authenticate(user=other_doctor)
        response = api_client.get("/api/patients/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["full_name"] == "Maria Sidorova"

    def test_doctor_without_organization_sees_nothing(
        self, api_client, doctor_without_org, patient
    ):
        api_client.force_authenticate(user=doctor_without_org)
        response = api_client.get("/api/patients/")
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_superuser_sees_all_patients(self, api_client, superuser, patient, other_patient):
        api_client.force_authenticate(user=superuser)
        response = api_client.get("/api/patients/")
        assert response.status_code == 200
        assert response.json()["count"] == 2


@pytest.mark.django_db
class TestPatientRetrieve:
    def test_doctor_can_retrieve_own_patient(self, api_client, doctor, patient):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/patients/{patient.id}/")
        assert response.status_code == 200
        assert response.json()["full_name"] == "Ivan Petrov"
        assert "age" in response.json()

    def test_doctor_cannot_retrieve_foreign_patient(self, api_client, doctor, other_patient):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/patients/{other_patient.id}/")
        assert response.status_code == 404

    def test_age_is_computed(self, api_client, doctor, patient):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/patients/{patient.id}/")
        today = date.today()
        expected_age = today.year - 1965
        if (today.month, today.day) < (3, 15):
            expected_age -= 1
        assert response.json()["age"] == expected_age


@pytest.mark.django_db
class TestPatientCreate:
    def test_doctor_can_create_in_own_organization(self, api_client, doctor, organization):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/patients/",
            {
                "organization": organization.id,
                "full_name": "New Patient",
                "birth_date": "1980-05-10",
                "sex": "male",
                "medical_record_number": "MRN-NEW-1",
                "contacts": {},
                "vital_status": "alive",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["full_name"] == "New Patient"

    def test_doctor_cannot_create_in_foreign_organization(
        self, api_client, doctor, other_organization
    ):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/patients/",
            {
                "organization": other_organization.id,
                "full_name": "Foreign",
                "birth_date": "1980-05-10",
                "sex": "male",
                "medical_record_number": "MRN-X",
                "vital_status": "alive",
            },
            format="json",
        )
        assert response.status_code == 400
        assert "organization" in response.json()

    def test_doctor_without_organization_cannot_create(
        self, api_client, doctor_without_org, organization
    ):
        api_client.force_authenticate(user=doctor_without_org)
        response = api_client.post(
            "/api/patients/",
            {
                "organization": organization.id,
                "full_name": "Nope",
                "birth_date": "1980-05-10",
                "sex": "male",
                "medical_record_number": "MRN-NOPE",
                "vital_status": "alive",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_superuser_can_create_in_any_organization(
        self, api_client, superuser, other_organization
    ):
        api_client.force_authenticate(user=superuser)
        response = api_client.post(
            "/api/patients/",
            {
                "organization": other_organization.id,
                "full_name": "Any Org Patient",
                "birth_date": "1980-05-10",
                "sex": "female",
                "medical_record_number": "MRN-ANY",
                "vital_status": "alive",
            },
            format="json",
        )
        assert response.status_code == 201


@pytest.mark.django_db
class TestPatientUpdate:
    def test_doctor_can_update_own_patient(self, api_client, doctor, patient):
        api_client.force_authenticate(user=doctor)
        response = api_client.patch(
            f"/api/patients/{patient.id}/",
            {"full_name": "Ivan Petrov Jr."},
            format="json",
        )
        assert response.status_code == 200
        patient.refresh_from_db()
        assert patient.full_name == "Ivan Petrov Jr."

    def test_doctor_cannot_update_foreign_patient(self, api_client, doctor, other_patient):
        api_client.force_authenticate(user=doctor)
        response = api_client.patch(
            f"/api/patients/{other_patient.id}/",
            {"full_name": "Hacked"},
            format="json",
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestPatientSearch:
    def test_search_by_full_name(self, api_client, doctor, organization):
        api_client.force_authenticate(user=doctor)
        Patient.objects.create(
            organization=organization,
            full_name="Alice Cooper",
            birth_date=date(1970, 1, 1),
            sex="female",
            medical_record_number="MRN-A",
        )
        Patient.objects.create(
            organization=organization,
            full_name="Bob Dylan",
            birth_date=date(1970, 1, 1),
            sex="male",
            medical_record_number="MRN-B",
        )
        response = api_client.get("/api/patients/?search=alice")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["full_name"] == "Alice Cooper"

    def test_search_by_mrn(self, api_client, doctor, patient):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/patients/?search=MRN-0001")
        assert response.status_code == 200
        assert response.json()["count"] == 1


@pytest.mark.django_db
class TestPatientPagination:
    def test_default_page_size_is_20(self, api_client, doctor, organization):
        api_client.force_authenticate(user=doctor)
        for i in range(25):
            Patient.objects.create(
                organization=organization,
                full_name=f"Patient {i:03d}",
                birth_date=date(1970, 1, 1),
                sex="male",
                medical_record_number=f"MRN-P-{i:04d}",
            )
        response = api_client.get("/api/patients/")
        data = response.json()
        assert data["count"] == 25
        assert len(data["results"]) == 20
        assert data["next"] is not None

    def test_page_size_query_param(self, api_client, doctor, organization):
        api_client.force_authenticate(user=doctor)
        for i in range(10):
            Patient.objects.create(
                organization=organization,
                full_name=f"Patient {i:03d}",
                birth_date=date(1970, 1, 1),
                sex="male",
                medical_record_number=f"MRN-PP-{i:04d}",
            )
        response = api_client.get("/api/patients/?page_size=5")
        data = response.json()
        assert data["count"] == 10
        assert len(data["results"]) == 5

    def test_second_page(self, api_client, doctor, organization):
        api_client.force_authenticate(user=doctor)
        for i in range(25):
            Patient.objects.create(
                organization=organization,
                full_name=f"Patient {i:03d}",
                birth_date=date(1970, 1, 1),
                sex="male",
                medical_record_number=f"MRN-P2-{i:04d}",
            )
        response = api_client.get("/api/patients/?page=2")
        data = response.json()
        assert data["count"] == 25
        assert len(data["results"]) == 5
        assert data["previous"] is not None
        assert data["next"] is None

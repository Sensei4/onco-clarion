from datetime import date

import pytest
from django.db import IntegrityError, transaction

from apps.patients.models import Patient


@pytest.mark.django_db
class TestPatientModel:
    def test_str_representation(self, patient):
        assert str(patient) == "Ivan Petrov (MRN-0001)"

    def test_birth_date_persisted(self, patient):
        assert patient.birth_date == date(1965, 3, 15)

    def test_default_vital_status_is_alive(self, db, organization):
        p = Patient.objects.create(
            organization=organization,
            full_name="Test",
            birth_date=date(1980, 1, 1),
            sex="male",
            medical_record_number="MRN-X",
        )
        assert p.vital_status == "alive"

    def test_contacts_defaults_to_empty_dict(self, db, organization):
        p = Patient.objects.create(
            organization=organization,
            full_name="Test",
            birth_date=date(1980, 1, 1),
            sex="male",
            medical_record_number="MRN-Y",
        )
        assert p.contacts == {}

    def test_mrn_must_be_unique_within_organization(self, db, organization, patient):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Patient.objects.create(
                    organization=organization,
                    full_name="Duplicate",
                    birth_date=date(1990, 1, 1),
                    sex="male",
                    medical_record_number="MRN-0001",
                )

    def test_mrn_can_repeat_across_organizations(self, patient, other_patient):
        assert patient.medical_record_number == other_patient.medical_record_number
        assert patient.organization != other_patient.organization

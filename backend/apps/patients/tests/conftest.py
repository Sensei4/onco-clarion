from datetime import date

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import Organization
from apps.patients.models import Patient

User = get_user_model()


@pytest.fixture
def organization(db):
    return Organization.objects.create(name="Org A", country="RU")


@pytest.fixture
def other_organization(db):
    return Organization.objects.create(name="Org B", country="KZ")


@pytest.fixture
def doctor(db, organization):
    return User.objects.create_user(
        username="doctor",
        password="strong-pass-12345",
        full_name="Doctor",
        role="doctor",
        organization=organization,
    )


@pytest.fixture
def other_doctor(db, other_organization):
    return User.objects.create_user(
        username="otherdoctor",
        password="strong-pass-12345",
        full_name="Other Doctor",
        role="doctor",
        organization=other_organization,
    )


@pytest.fixture
def doctor_without_org(db):
    return User.objects.create_user(
        username="noorg",
        password="strong-pass-12345",
        full_name="No Org Doctor",
        role="doctor",
    )


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username="super",
        password="strong-pass-12345",
        email="super@example.com",
    )


@pytest.fixture
def patient(db, organization):
    return Patient.objects.create(
        organization=organization,
        full_name="Ivan Petrov",
        birth_date=date(1965, 3, 15),
        sex="male",
        medical_record_number="MRN-0001",
        contacts={"phone": "+7-900-000-00-01"},
        vital_status="alive",
    )


@pytest.fixture
def other_patient(db, other_organization):
    return Patient.objects.create(
        organization=other_organization,
        full_name="Maria Sidorova",
        birth_date=date(1975, 6, 20),
        sex="female",
        medical_record_number="MRN-0001",
        contacts={},
        vital_status="alive",
    )

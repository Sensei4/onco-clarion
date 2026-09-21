from datetime import date

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import Organization
from apps.cases.models import CancerCase
from apps.patients.models import Patient
from apps.referrals.models import Referral

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
        role="doctor",
        organization=organization,
    )


@pytest.fixture
def other_doctor(db, other_organization):
    return User.objects.create_user(
        username="otherdoctor",
        password="strong-pass-12345",
        role="doctor",
        organization=other_organization,
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
    )


@pytest.fixture
def other_patient(db, other_organization):
    return Patient.objects.create(
        organization=other_organization,
        full_name="Maria Sidorova",
        birth_date=date(1975, 6, 20),
        sex="female",
        medical_record_number="MRN-0002",
    )


@pytest.fixture
def case(db, organization, patient):
    return CancerCase.objects.create(
        patient=patient,
        organization=organization,
        diagnosis_code="C50.9",
    )


@pytest.fixture
def other_case(db, other_organization, other_patient):
    return CancerCase.objects.create(
        patient=other_patient,
        organization=other_organization,
        diagnosis_code="C34.9",
    )


@pytest.fixture
def referral(db, case, organization, doctor):
    return Referral.objects.create(
        case=case,
        organization=organization,
        type=Referral.Type.IMAGING,
        title="CT chest with contrast",
        ordered_by=doctor,
    )


@pytest.fixture
def other_referral(db, other_case, other_organization, other_doctor):
    return Referral.objects.create(
        case=other_case,
        organization=other_organization,
        type=Referral.Type.LAB,
        title="CBC",
        ordered_by=other_doctor,
    )

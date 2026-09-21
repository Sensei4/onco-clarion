from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.models import Organization
from apps.cases.models import CancerCase
from apps.documents.models import Document
from apps.patients.models import Patient

User = get_user_model()


def make_pdf(name: str = "test.pdf") -> SimpleUploadedFile:
    """Create a tiny in-memory PDF for upload tests."""
    content = b"%PDF-1.4\n%Test PDF for OncoClarion\n%%EOF"
    return SimpleUploadedFile(name, content, content_type="application/pdf")


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
def document(db, case, organization, doctor):
    return Document.objects.create(
        case=case,
        organization=organization,
        type=Document.Type.HISTOLOGY,
        title="Histology report",
        file=make_pdf("histology.pdf"),
        uploaded_by=doctor,
    )


@pytest.fixture
def other_document(db, other_case, other_organization, other_doctor):
    return Document.objects.create(
        case=other_case,
        organization=other_organization,
        type=Document.Type.ANALYSIS,
        title="CBC result",
        file=make_pdf("cbc.pdf"),
        uploaded_by=other_doctor,
    )

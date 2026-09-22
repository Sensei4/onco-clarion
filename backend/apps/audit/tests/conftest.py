import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import Organization
from apps.audit.models import AuditEvent

User = get_user_model()


@pytest.fixture
def organization(db):
    return Organization.objects.create(name="Org A", country="RU")


@pytest.fixture
def other_organization(db):
    return Organization.objects.create(name="Org B", country="KZ")


@pytest.fixture
def admin_user(db, organization):
    return User.objects.create_user(
        username="admin1",
        password="strong-pass-12345",
        role="admin",
        organization=organization,
    )


@pytest.fixture
def other_admin(db, other_organization):
    return User.objects.create_user(
        username="admin2",
        password="strong-pass-12345",
        role="admin",
        organization=other_organization,
    )


@pytest.fixture
def doctor(db, organization):
    return User.objects.create_user(
        username="doctor1",
        password="strong-pass-12345",
        role="doctor",
        organization=organization,
    )


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username="super",
        password="strong-pass-12345",
        email="super@example.com",
    )


@pytest.fixture
def event_in_org_a(db, organization, admin_user):
    return AuditEvent.objects.create(
        user=admin_user,
        action=AuditEvent.Action.VIEW,
        entity_type="Patient",
        entity_id=1,
        entity_repr="Ivan Petrov (MRN-0001)",
        organization=organization,
        ip_address="10.0.0.1",
        request_method="GET",
        request_path="/api/patients/1/",
    )


@pytest.fixture
def event_in_org_b(db, other_organization, other_admin):
    return AuditEvent.objects.create(
        user=other_admin,
        action=AuditEvent.Action.VIEW,
        entity_type="Patient",
        entity_id=2,
        entity_repr="Maria Sidorova (MRN-0002)",
        organization=other_organization,
        ip_address="10.0.0.2",
        request_method="GET",
        request_path="/api/patients/2/",
    )


@pytest.fixture
def download_event(db, organization, admin_user):
    return AuditEvent.objects.create(
        user=admin_user,
        action=AuditEvent.Action.DOWNLOAD,
        entity_type="Document",
        entity_id=1,
        entity_repr="Histology",
        organization=organization,
        ip_address="10.0.0.1",
        request_method="GET",
        request_path="/api/documents/1/download/",
    )

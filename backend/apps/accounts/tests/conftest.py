import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import Organization

User = get_user_model()


@pytest.fixture
def organization(db):
    """A test organization."""
    return Organization.objects.create(
        name="Test Oncology Center",
        country="RU",
    )


@pytest.fixture
def other_organization(db):
    """A second organization for multi-tenancy tests."""
    return Organization.objects.create(
        name="Other Center",
        country="RU",
    )


@pytest.fixture
def admin_user(db, organization):
    """A user with role=admin, attached to `organization`."""
    return User.objects.create_user(
        username="admin1",
        password="strong-pass-12345",
        full_name="Admin One",
        role="admin",
        organization=organization,
    )


@pytest.fixture
def doctor_user(db, organization):
    """A regular doctor attached to `organization`."""
    return User.objects.create_user(
        username="doctor1",
        password="strong-pass-12345",
        full_name="Doctor One",
        role="doctor",
        organization=organization,
    )


@pytest.fixture
def superuser(db):
    """A Django superuser without organization."""
    return User.objects.create_superuser(
        username="super1",
        password="strong-pass-12345",
        email="super@example.com",
    )

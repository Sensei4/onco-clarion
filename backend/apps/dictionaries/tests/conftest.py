import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.models import Organization
from apps.dictionaries.models import FoundationEntity, MmsEntity

User = get_user_model()


@pytest.fixture
def organization(db):
    return Organization.objects.create(name="Org A", country="RU")


@pytest.fixture
def doctor(db, organization):
    return User.objects.create_user(
        username="doctor",
        password="strong-pass-12345",
        role="doctor",
        organization=organization,
    )


@pytest.fixture
def mms_breast(db):
    """A real-looking MMS entity for breast cancer."""
    return MmsEntity.objects.create(
        uri="http://id.who.int/icd/release/11/2026-01/mms/1047754165/unspecified",
        foundation_uri="http://id.who.int/icd/entity/1047754165",
        the_code="2C6Z",
        title="Malignant neoplasms of breast, unspecified",
        chapter="02",
        is_leaf=True,
        is_residual_unspecified=True,
        synonyms=["breast cancer", "cancer of breast"],
        last_synced_at=timezone.now(),
    )


@pytest.fixture
def mms_ductal(db):
    return MmsEntity.objects.create(
        uri="http://id.who.int/icd/release/11/2026-01/mms/175963120",
        foundation_uri="http://id.who.int/icd/entity/175963120",
        the_code="2C61.0",
        title="Invasive ductal carcinoma of breast",
        chapter="02",
        is_leaf=True,
        synonyms=["infiltrating ductal carcinoma"],
        last_synced_at=timezone.now(),
    )


@pytest.fixture
def mms_parent_without_code(db):
    """A parent node without a code (like 'Malignant neoplasms of breast')."""
    return MmsEntity.objects.create(
        uri="http://id.who.int/icd/release/11/2026-01/mms/1047754165",
        foundation_uri="http://id.who.int/icd/entity/1047754165",
        the_code="",
        title="Malignant neoplasms of breast",
        chapter="02",
        is_leaf=False,
        synonyms=["breast cancer"],
        last_synced_at=timezone.now(),
    )


@pytest.fixture
def foundation_breast(db):
    return FoundationEntity.objects.create(
        uri="http://id.who.int/icd/entity/1047754165",
        title="Malignant neoplasms of breast",
        definition="Malignant neoplasms of the breast.",
        long_definition="",
        synonyms=["breast cancer", "cancer of breast", "malignant tumour of breast"],
        parent_uris=[],
        child_uris=[],
        exclusions=[],
        browser_url="https://icd.who.int/browse/2026-01/foundation/en#1047754165",
        chapter="",
        last_synced_at=timezone.now(),
    )

"""Mapper: User model → FHIR R4B Practitioner resource."""

from django.contrib.auth import get_user_model
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.practitioner import Practitioner as FHIRPractitioner

from .common import (
    SYSTEM_USERNAME,
    split_full_name,
)

User = get_user_model()


def to_fhir(user: User) -> FHIRPractitioner:
    """Convert a User model to a FHIR R4B Practitioner resource."""
    display_name = user.full_name or user.username
    name_parts = split_full_name(display_name)

    fhir_name = HumanName(
        text=display_name,
        family=name_parts["family"] or None,
        given=name_parts["given"] or None,
    )

    identifier = Identifier(
        system=SYSTEM_USERNAME,
        value=user.username,
    )

    return FHIRPractitioner(
        id=str(user.id),
        identifier=[identifier],
        name=[fhir_name],
        active=user.is_active,
    )

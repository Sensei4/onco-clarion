"""Mapper: Patient model → FHIR R4B Patient resource."""

from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.patient import Patient as FHIRPatient

from apps.patients.models import Patient

from .common import (
    SYSTEM_MRN,
    format_date,
    split_full_name,
)


def to_fhir(patient: Patient) -> FHIRPatient:
    """Convert a Patient model to a FHIR R4B Patient resource."""
    name_parts = split_full_name(patient.full_name)

    fhir_name = HumanName(
        text=patient.full_name,
        family=name_parts["family"] or None,
        given=name_parts["given"] or None,
    )

    identifier = Identifier(
        system=SYSTEM_MRN,
        value=patient.medical_record_number,
    )

    data: dict = {
        "id": str(patient.id),
        "active": patient.vital_status == Patient.VitalStatus.ALIVE,
        "identifier": [identifier],
        "name": [fhir_name],
        "gender": _map_gender(patient.sex),
    }

    birth_date = format_date(patient.birth_date)
    if birth_date:
        data["birthDate"] = birth_date

    if patient.vital_status == Patient.VitalStatus.DEAD:
        data["deceasedBoolean"] = True

    return FHIRPatient(**data)


def _map_gender(sex: str) -> str | None:
    """Map our Sex enum to FHIR gender values.

    FHIR gender: male | female | other | unknown
    We already use the same values, so it's a direct mapping.
    """
    if sex in ("male", "female", "other", "unknown"):
        return sex
    return "unknown"

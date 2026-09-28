"""Mapper: CancerCase model → FHIR R4B Condition resource."""

from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.condition import Condition as FHIRCondition
from fhir.resources.R4B.reference import Reference

from apps.cases.models import CancerCase

from .common import (
    SYSTEM_ICD11_MMS,
    format_date,
)

# Mapping of our FSM statuses to FHIR clinical status codes.
# FHIR clinical status: active | recurrence | relapse | inactive | remission | resolved
_STATUS_MAP: dict[str, str] = {
    CancerCase.Status.NEW: "active",
    CancerCase.Status.DIAGNOSTIC: "active",
    CancerCase.Status.CONSILIUM: "active",
    CancerCase.Status.WAITING_HOSPITALIZATION: "active",
    CancerCase.Status.IN_TREATMENT: "active",
    CancerCase.Status.OBSERVATION: "active",
    CancerCase.Status.REMISSION: "remission",
    CancerCase.Status.RELAPSE: "relapse",
    CancerCase.Status.TERMINAL: "resolved",
}


def to_fhir(case: CancerCase) -> FHIRCondition:
    """Convert a CancerCase model to a FHIR R4B Condition resource."""
    # Subject: reference to the Patient resource
    subject = Reference(reference=f"Patient/{case.patient_id}")

    # Code: ICD-11 MMS coding + human-readable text
    code_text = case.diagnosis_text or case.diagnosis_code or f"Case #{case.id}"
    code = CodeableConcept(text=code_text)

    if case.icd11_mms_uri and case.diagnosis_code:
        coding = Coding(
            system=SYSTEM_ICD11_MMS,
            code=case.diagnosis_code,
            display=case.diagnosis_text or None,
        )
        code.coding = [coding]

    # Clinical status: active / remission / relapse / resolved
    status_code = _STATUS_MAP.get(case.status, "active")
    clinical_status = CodeableConcept(
        text=status_code,
        coding=[
            Coding(
                system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                code=status_code,
            )
        ],
    )

    data: dict = {
        "id": str(case.id),
        "subject": subject,
        "code": code,
        "clinicalStatus": clinical_status,
    }

    recorded = format_date(case.verification_date)
    if recorded:
        data["recordedDate"] = recorded

    return FHIRCondition(**data)

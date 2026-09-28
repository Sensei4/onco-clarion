"""Mapper: Event model → FHIR R4B Encounter resource."""

from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.encounter import Encounter as FHIREncounter
from fhir.resources.R4B.period import Period
from fhir.resources.R4B.reference import Reference

from apps.events.models import Event

from .common import format_datetime

# Mapping of our event types to FHIR Encounter class codes.
# FHIR Encounter.class: AMB (ambulatory), IMP (inpatient), EMER (emergency),
#                       VR (virtual), HH (home health), etc.
_CLASS_MAP: dict[str, str] = {
    Event.Type.PRIMARY_VISIT: "AMB",
    Event.Type.FOLLOWUP_VISIT: "AMB",
    Event.Type.OBSERVATION_VISIT: "AMB",
    Event.Type.CONSILIUM: "AMB",
    Event.Type.HOSPITALIZATION: "IMP",
    Event.Type.TREATMENT: "AMB",  # treatment can be ambulatory; specifics later
}


def to_fhir(event: Event) -> FHIREncounter:
    """Convert an Event model to a FHIR R4B Encounter resource."""
    # Subject: the patient
    subject = Reference(reference=f"Patient/{event.patient_id}")

    # Reason: the cancer case (as a Condition reference)
    reason = Reference(reference=f"Condition/{event.case_id}")

    # Class: our type → FHIR class code
    class_code = _CLASS_MAP.get(event.type, "AMB")
    fhir_class = Coding(
        system="http://terminology.hl7.org/CodeSystem/v3-ActCode",
        code=class_code,
    )

    # Period: scheduled → start, occurred → end
    start = format_datetime(event.scheduled_at)
    end = format_datetime(event.occurred_at) if event.occurred_at else None
    period = None
    if start or end:
        period = Period(start=start, end=end)

    data: dict = {
        "id": str(event.id),
        "status": _map_status(event.status),
        "class": fhir_class,
        "subject": subject,
        "reasonReference": [reason],
    }

    if period:
        data["period"] = period

    # Author as participant
    if event.author_id:
        participant = {
            "individual": Reference(reference=f"Practitioner/{event.author_id}"),
        }
        data["participant"] = [participant]

    # Notes → Encounter.text (Narrative), since Encounter has no `note` field in R4B
    if event.notes:
        data["text"] = {
            "status": "generated",
            "div": f"<div xmlns='http://www.w3.org/1999/xhtml'>{event.notes}</div>",
        }

    return FHIREncounter(**data)


def _map_status(status: str) -> str:
    """Map our Event status to FHIR Encounter.status.

    FHIR Encounter.status: planned | arrived | triaged | in-progress |
                           onleave | finished | cancelled | entered-in-error | unknown
    """
    return {
        Event.Status.PLANNED: "planned",
        Event.Status.DONE: "finished",
        Event.Status.CANCELLED: "cancelled",
    }.get(status, "unknown")

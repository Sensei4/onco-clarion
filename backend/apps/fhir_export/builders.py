"""Builders for FHIR Bundle resources."""

from django.contrib.auth import get_user_model
from fhir.resources.R4B.bundle import Bundle, BundleEntry

from apps.cases.models import CancerCase
from apps.events.models import Event
from apps.patients.models import Patient

from .mappers.condition import to_fhir as case_to_fhir
from .mappers.encounter import to_fhir as event_to_fhir
from .mappers.patient import to_fhir as patient_to_fhir
from .mappers.practitioner import to_fhir as user_to_fhir

User = get_user_model()


def build_patient_everything(patient: Patient) -> Bundle:
    """Build a Bundle containing Patient + Conditions + Encounters + Practitioners.

    The Bundle follows the FHIR `$everything` convention:
    - Patient resource
    - All Conditions of the patient
    - All Encounters of the patient
    - All Practitioners who authored at least one Encounter

    Bundle.type is "collection" (this is not a transaction).
    """
    entries: list[BundleEntry] = []
    seen_practitioner_ids: set[int] = set()

    # 1. Patient
    fhir_patient = patient_to_fhir(patient)
    entries.append(
        BundleEntry(
            fullUrl=f"Patient/{fhir_patient.id}",
            resource=fhir_patient,
        )
    )

    # 2. Conditions (all CancerCases)
    cases = CancerCase.objects.filter(patient=patient).order_by("created_at")
    for case in cases:
        fhir_condition = case_to_fhir(case)
        entries.append(
            BundleEntry(
                fullUrl=f"Condition/{fhir_condition.id}",
                resource=fhir_condition,
            )
        )

    # 3. Encounters (all Events)
    events = Event.objects.filter(patient=patient).select_related("author").order_by("scheduled_at")
    for event in events:
        fhir_encounter = event_to_fhir(event)
        entries.append(
            BundleEntry(
                fullUrl=f"Encounter/{fhir_encounter.id}",
                resource=fhir_encounter,
            )
        )
        if event.author_id:
            seen_practitioner_ids.add(event.author_id)

    # 4. Practitioners (dedup)
    if seen_practitioner_ids:
        users = User.objects.filter(id__in=seen_practitioner_ids)
        for user in users:
            fhir_practitioner = user_to_fhir(user)
            entries.append(
                BundleEntry(
                    fullUrl=f"Practitioner/{fhir_practitioner.id}",
                    resource=fhir_practitioner,
                )
            )

    return Bundle(
        type="collection",
        total=len(entries),
        entry=entries,
    )

"""FHIR export endpoints.

All endpoints require admin role. Every export is logged to AuditEvent.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.audit.mixins import log_custom_action
from apps.audit.models import AuditEvent
from apps.patients.models import Patient

from .builders import build_patient_everything
from .mappers.patient import to_fhir as patient_to_fhir
from .permissions import IsAdminUser


@api_view(["GET"])
@permission_classes([IsAdminUser])
def patient_fhir(request, pk: int):
    """Export a single Patient as a FHIR R4B resource."""
    patient = get_object_or_404(Patient, pk=pk)

    log_custom_action(
        request,
        patient,
        AuditEvent.Action.EXPORT,
    )

    fhir_patient = patient_to_fhir(patient)
    return Response(
        fhir_patient.model_dump(exclude_none=True),
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def patient_everything(request, pk: int):
    """Export a Patient with all related resources as a FHIR Bundle.

    Includes: Patient, Conditions, Encounters, Practitioners.
    """
    patient = get_object_or_404(Patient, pk=pk)

    log_custom_action(
        request,
        patient,
        AuditEvent.Action.EXPORT,
    )

    bundle = build_patient_everything(patient)
    return Response(
        bundle.model_dump(exclude_none=True),
        status=status.HTTP_200_OK,
    )

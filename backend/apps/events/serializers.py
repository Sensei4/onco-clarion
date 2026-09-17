from rest_framework import serializers

from .models import (
    Event,
    EventConsilium,
    EventFollowupVisit,
    EventHospitalization,
    EventObservationVisit,
    EventPrimaryVisit,
    EventTreatment,
)


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for event lists and timelines.

    Returns base fields only. Subtype-specific fields are not included
    (fetch /api/events/{id}/ for full details).
    """

    case_diagnosis = serializers.CharField(
        source="case.diagnosis_code",
        read_only=True,
    )
    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True,
    )
    patient_mrn = serializers.CharField(
        source="patient.medical_record_number",
        read_only=True,
    )
    author_name = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    class Meta:
        model = Event
        fields = (
            "id",
            "type",
            "status",
            "case",
            "case_diagnosis",
            "patient",
            "patient_name",
            "patient_mrn",
            "organization",
            "scheduled_at",
            "occurred_at",
            "author",
            "author_name",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class EventDetailSerializer(serializers.ModelSerializer):
    """Full event serializer with subtype-specific fields.

    Uses `to_representation` to attach subtype fields dynamically
    based on `event.type`.
    """

    case_diagnosis = serializers.CharField(
        source="case.diagnosis_code",
        read_only=True,
    )
    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True,
    )
    patient_mrn = serializers.CharField(
        source="patient.medical_record_number",
        read_only=True,
    )
    author_name = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    class Meta:
        model = Event
        fields = (
            "id",
            "type",
            "status",
            "case",
            "case_diagnosis",
            "patient",
            "patient_name",
            "patient_mrn",
            "organization",
            "scheduled_at",
            "occurred_at",
            "author",
            "author_name",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def to_representation(self, instance: Event) -> dict:
        data = super().to_representation(instance)
        data["details"] = _get_subtype_data(instance)
        return data


def _get_subtype_data(event: Event) -> dict | None:
    """Return subtype-specific fields for the event, or None."""
    try:
        if event.type == Event.Type.PRIMARY_VISIT:
            sub = event.eventprimaryvisit
            return {
                "chief_complaint": sub.chief_complaint,
                "physical_exam": sub.physical_exam,
            }
        if event.type == Event.Type.FOLLOWUP_VISIT:
            sub = event.eventfollowupvisit
            return {
                "findings": sub.findings,
                "plan": sub.plan,
            }
        if event.type == Event.Type.OBSERVATION_VISIT:
            sub = event.eventobservationvisit
            return {
                "findings": sub.findings,
            }
        if event.type == Event.Type.CONSILIUM:
            sub = event.eventconsilium
            return {
                "participants": list(sub.participants.values_list("id", flat=True)),
                "participant_names": list(sub.participants.values_list("username", flat=True)),
                "decision": sub.decision,
                "recommended_plan": sub.recommended_plan,
            }
        if event.type == Event.Type.HOSPITALIZATION:
            sub = event.eventhospitalization
            return {
                "ward": sub.ward,
                "reason": sub.reason,
                "discharge_date": sub.discharge_date,
            }
        if event.type == Event.Type.TREATMENT:
            sub = event.eventtreatment
            return {
                "modality": sub.modality,
                "regimen": sub.regimen,
                "cycle_number": sub.cycle_number,
                "cycle_total": sub.cycle_total,
                "drugs": sub.drugs,
            }
    except Event.DoesNotExist:
        # Defensive: base Event exists but subtype row missing
        return None
    return None


# ---------------------------------------------------------------------------
# Subtype-specific create/update serializers
# ---------------------------------------------------------------------------


class EventPrimaryVisitWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPrimaryVisit
        fields = (
            "id",
            "case",
            "patient",
            "organization",
            "status",
            "scheduled_at",
            "occurred_at",
            "author",
            "notes",
            "chief_complaint",
            "physical_exam",
        )
        read_only_fields = ("id", "author")

    def create(self, validated_data):
        validated_data["type"] = Event.Type.PRIMARY_VISIT
        return super().create(validated_data)


class EventFollowupVisitWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventFollowupVisit
        fields = (
            "id",
            "case",
            "patient",
            "organization",
            "status",
            "scheduled_at",
            "occurred_at",
            "author",
            "notes",
            "findings",
            "plan",
        )
        read_only_fields = ("id", "author")

    def create(self, validated_data):
        validated_data["type"] = Event.Type.FOLLOWUP_VISIT
        return super().create(validated_data)


class EventObservationVisitWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventObservationVisit
        fields = (
            "id",
            "case",
            "patient",
            "organization",
            "status",
            "scheduled_at",
            "occurred_at",
            "author",
            "notes",
            "findings",
        )
        read_only_fields = ("id", "author")

    def create(self, validated_data):
        validated_data["type"] = Event.Type.OBSERVATION_VISIT
        return super().create(validated_data)


class EventConsiliumWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventConsilium
        fields = (
            "id",
            "case",
            "patient",
            "organization",
            "status",
            "scheduled_at",
            "occurred_at",
            "author",
            "notes",
            "participants",
            "decision",
            "recommended_plan",
        )
        read_only_fields = ("id", "author")

    def create(self, validated_data):
        validated_data["type"] = Event.Type.CONSILIUM
        return super().create(validated_data)


class EventHospitalizationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventHospitalization
        fields = (
            "id",
            "case",
            "patient",
            "organization",
            "status",
            "scheduled_at",
            "occurred_at",
            "author",
            "notes",
            "ward",
            "reason",
            "discharge_date",
        )
        read_only_fields = ("id", "author")

    def create(self, validated_data):
        validated_data["type"] = Event.Type.HOSPITALIZATION
        return super().create(validated_data)


class EventTreatmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTreatment
        fields = (
            "id",
            "case",
            "patient",
            "organization",
            "status",
            "scheduled_at",
            "occurred_at",
            "author",
            "notes",
            "modality",
            "regimen",
            "cycle_number",
            "cycle_total",
            "drugs",
        )
        read_only_fields = ("id", "author")

    def create(self, validated_data):
        validated_data["type"] = Event.Type.TREATMENT
        return super().create(validated_data)

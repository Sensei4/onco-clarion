from rest_framework import serializers

from .models import Referral


class ReferralListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lists and case sections."""

    case_diagnosis = serializers.CharField(
        source="case.diagnosis_code",
        read_only=True,
    )
    patient_name = serializers.CharField(
        source="case.patient.full_name",
        read_only=True,
    )
    patient_mrn = serializers.CharField(
        source="case.patient.medical_record_number",
        read_only=True,
    )
    ordered_by_name = serializers.CharField(
        source="ordered_by.username",
        read_only=True,
    )

    class Meta:
        model = Referral
        fields = (
            "id",
            "case",
            "case_diagnosis",
            "patient_name",
            "patient_mrn",
            "event",
            "organization",
            "type",
            "status",
            "title",
            "ordered_by",
            "ordered_by_name",
            "ordered_at",
            "result_received_at",
        )
        read_only_fields = fields


class ReferralDetailSerializer(serializers.ModelSerializer):
    """Full serializer for retrieve, create, update."""

    case_diagnosis = serializers.CharField(
        source="case.diagnosis_code",
        read_only=True,
    )
    patient_name = serializers.CharField(
        source="case.patient.full_name",
        read_only=True,
    )
    patient_mrn = serializers.CharField(
        source="case.patient.medical_record_number",
        read_only=True,
    )
    ordered_by_name = serializers.CharField(
        source="ordered_by.username",
        read_only=True,
    )
    completed_by_name = serializers.CharField(
        source="completed_by.username",
        read_only=True,
        default=None,
    )

    class Meta:
        model = Referral
        fields = (
            "id",
            "case",
            "case_diagnosis",
            "patient_name",
            "patient_mrn",
            "event",
            "organization",
            "type",
            "status",
            "title",
            "notes",
            "ordered_by",
            "ordered_by_name",
            "ordered_at",
            "result_text",
            "result_received_at",
            "completed_by",
            "completed_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "ordered_by",
            "ordered_at",
            "result_received_at",
            "completed_by",
            "created_at",
            "updated_at",
        )

    def validate_case(self, value):
        """Ensure the user can only create referrals for cases in their org."""
        request = self.context.get("request")
        if request is None:
            return value
        user = request.user
        if user.is_superuser:
            return value
        if value.organization_id != user.organization_id:
            raise serializers.ValidationError(
                "You can only create referrals for cases in your organization."
            )
        return value


class CompleteReferralSerializer(serializers.Serializer):
    """Input for POST /api/referrals/{id}/complete/."""

    result_text = serializers.CharField(required=False, allow_blank=True, default="")


class CancelReferralSerializer(serializers.Serializer):
    """Input for POST /api/referrals/{id}/cancel/."""

    reason = serializers.CharField(required=False, allow_blank=True, default="")

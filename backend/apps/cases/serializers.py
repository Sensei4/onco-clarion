from rest_framework import serializers

from .models import CancerCase, StatusTransition


class CancerCaseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoints."""

    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True,
    )
    patient_mrn = serializers.CharField(
        source="patient.medical_record_number",
        read_only=True,
    )
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    class Meta:
        model = CancerCase
        fields = (
            "id",
            "patient",
            "patient_name",
            "patient_mrn",
            "organization",
            "organization_name",
            "diagnosis_code",
            "icd11_mms_uri",
            "stage",
            "status",
            "created_at",
        )
        read_only_fields = fields


class CancerCaseDetailSerializer(serializers.ModelSerializer):
    """Full serializer for retrieve, create, and update."""

    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True,
    )
    patient_mrn = serializers.CharField(
        source="patient.medical_record_number",
        read_only=True,
    )
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    class Meta:
        model = CancerCase
        fields = (
            "id",
            "patient",
            "patient_name",
            "patient_mrn",
            "organization",
            "organization_name",
            "diagnosis_code",
            "diagnosis_text",
            "icd11_mms_uri",
            "verification_date",
            "tnm_t",
            "tnm_n",
            "tnm_m",
            "stage",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",  # only transitions can change status
            "created_at",
            "updated_at",
        )

    def validate_organization(self, value):
        """Ensure the user can only assign cases within their organization."""
        request = self.context.get("request")
        if request is None:
            return value
        user = request.user
        if user.is_superuser:
            return value
        if user.organization_id != value.id:
            raise serializers.ValidationError("You can only create cases in your own organization.")
        return value

    def validate_patient(self, value):
        """Ensure the patient belongs to the same organization as the case."""
        organization = self.initial_data.get("organization")
        if organization is None and self.instance is not None:
            return value
        if organization is None:
            return value
        if str(value.organization_id) != str(organization):
            raise serializers.ValidationError(
                "Patient must belong to the same organization as the case."
            )
        return value


class StatusTransitionSerializer(serializers.ModelSerializer):
    """Read-only serializer for audit records."""

    transitioned_by_name = serializers.CharField(
        source="transitioned_by.username",
        read_only=True,
        default=None,
    )

    class Meta:
        model = StatusTransition
        fields = (
            "id",
            "from_status",
            "to_status",
            "transitioned_by",
            "transitioned_by_name",
            "transitioned_at",
            "reason",
        )
        read_only_fields = fields


class TransitionActionSerializer(serializers.Serializer):
    """Input for POST /api/cases/{id}/transition/."""

    action = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_action(self, value: str) -> str:
        """Check that `action` is a valid transition method on CancerCase."""
        if not hasattr(CancerCase, value):
            raise serializers.ValidationError(f"Unknown action: '{value}'.")
        method = getattr(CancerCase, value)
        # Transition methods are decorated and carry a `_django_fsm` attribute
        if not hasattr(method, "_django_fsm"):
            raise serializers.ValidationError(f"'{value}' is not a transition action.")
        return value

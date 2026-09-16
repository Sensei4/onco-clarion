from rest_framework import serializers

from .models import CancerCase


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

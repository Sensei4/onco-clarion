from rest_framework import serializers

from .models import (
    DiagnosticDepartment,
    DiagnosticMethod,
    Referral,
)


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
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
        default=None,
    )
    method_name = serializers.CharField(
        source="method.name",
        read_only=True,
        default=None,
    )
    assigned_to_name = serializers.CharField(
        source="assigned_to.username",
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
            "department",
            "department_name",
            "method",
            "method_name",
            "assigned_to",
            "assigned_to_name",
            "scheduled_at",
            "room",
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
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
        default=None,
    )
    method_name = serializers.CharField(
        source="method.name",
        read_only=True,
        default=None,
    )
    assigned_to_name = serializers.CharField(
        source="assigned_to.username",
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
            "department",
            "department_name",
            "method",
            "method_name",
            "assigned_to",
            "assigned_to_name",
            "scheduled_at",
            "room",
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

    def validate_department(self, value):
        """Ensure the department belongs to the user's organization."""
        if value is None:
            return value
        request = self.context.get("request")
        if request is None:
            return value
        user = request.user
        if user.is_superuser:
            return value
        if value.organization_id != user.organization_id:
            raise serializers.ValidationError("Department must belong to your organization.")
        return value

    def validate(self, attrs):
        """Cross-field validation: method must belong to department."""
        department = attrs.get(
            "department",
            getattr(self.instance, "department", None),
        )
        method = attrs.get(
            "method",
            getattr(self.instance, "method", None),
        )

        if method is not None and department is not None:
            if method.department_id != department.id:
                raise serializers.ValidationError(
                    {"method": "Method does not belong to the selected department."}
                )

        return attrs

    def create(self, validated_data):
        """Auto-fill type and title from department/method if not provided."""
        request = self.context.get("request")
        if request is not None and "ordered_by" not in validated_data:
            validated_data["ordered_by"] = request.user

        department: DiagnosticDepartment | None = validated_data.get("department")
        method: DiagnosticMethod | None = validated_data.get("method")

        # Auto-fill type from department category if not provided
        if not validated_data.get("type") and department is not None:
            validated_data["type"] = _category_to_type(department.category)

        # Auto-fill title from method name if not provided
        if not validated_data.get("title") and method is not None:
            validated_data["title"] = method.name

        return super().create(validated_data)


def _category_to_type(category: str) -> str:
    """Map a department category to a Referral.Type value.

    Used for backwards-compatible filtering: department.category →
    Referral.type. Only imaging / laboratory / pathology have direct
    matches; everything else maps to "other".
    """
    mapping = {
        DiagnosticDepartment.Category.LABORATORY: Referral.Type.LAB,
        DiagnosticDepartment.Category.PATHOLOGY: Referral.Type.HISTOLOGY,
        DiagnosticDepartment.Category.IMAGING: Referral.Type.IMAGING,
        DiagnosticDepartment.Category.MOLECULAR: Referral.Type.LAB,
        DiagnosticDepartment.Category.ENDOSCOPY: Referral.Type.OTHER,
        DiagnosticDepartment.Category.FUNCTIONAL: Referral.Type.OTHER,
        DiagnosticDepartment.Category.SURGERY: Referral.Type.OTHER,
        DiagnosticDepartment.Category.OTHER: Referral.Type.OTHER,
    }
    return mapping.get(category, Referral.Type.OTHER)


class CompleteReferralSerializer(serializers.Serializer):
    """Input for POST /api/referrals/{id}/complete/."""

    result_text = serializers.CharField(required=False, allow_blank=True, default="")


class CancelReferralSerializer(serializers.Serializer):
    """Input for POST /api/referrals/{id}/cancel/."""

    reason = serializers.CharField(required=False, allow_blank=True, default="")

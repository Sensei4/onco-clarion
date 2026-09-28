from datetime import date

from django.db.models import Min
from rest_framework import serializers

from apps.accounts.models import Organization

from .models import Patient


class PatientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoints.

    Includes computed fields:
    - age: computed from birth_date
    - first_diagnosis_date: earliest verification_date across all cases
    """

    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )
    age = serializers.SerializerMethodField()
    first_diagnosis_date = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "id",
            "full_name",
            "medical_record_number",
            "birth_date",
            "age",
            "sex",
            "vital_status",
            "death_date",
            "insurance_policy_number",
            "first_diagnosis_date",
            "organization",
            "organization_name",
            "created_at",
        )
        read_only_fields = fields

    def get_age(self, obj: Patient) -> int | None:
        if not obj.birth_date:
            return None
        today = date.today()
        years = today.year - obj.birth_date.year
        if (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day):
            years -= 1
        return years

    def get_first_diagnosis_date(self, obj: Patient) -> str | None:
        """Earliest verification_date across all cancer cases of this patient.

        Uses annotation if available (annotated as `_first_diagnosis_date`),
        otherwise falls back to a query.
        """
        annotated = getattr(obj, "_first_diagnosis_date", None)
        if annotated is not None:
            return annotated.isoformat() if annotated else None

        # Fallback if annotation wasn't applied
        result = obj.cases.aggregate(first=Min("verification_date"))["first"]
        return result.isoformat() if result else None


class PatientDetailSerializer(serializers.ModelSerializer):
    """Full serializer for retrieve, create, and update."""

    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "id",
            "organization",
            "organization_name",
            "full_name",
            "birth_date",
            "age",
            "sex",
            "medical_record_number",
            "contacts",
            "insurance_policy_number",
            "death_date",
            "vital_status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_age(self, obj: Patient) -> int | None:
        if not obj.birth_date:
            return None
        today = date.today()
        years = today.year - obj.birth_date.year
        if (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day):
            years -= 1
        return years

    def validate_organization(self, value: Organization) -> Organization:
        request = self.context.get("request")
        if request is None:
            return value

        user = request.user
        if user.is_superuser:
            return value

        if user.organization_id != value.id:
            raise serializers.ValidationError(
                "You can only create patients in your own organization."
            )
        return value

from rest_framework import serializers

from apps.accounts.models import Organization

from .models import Patient


class PatientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoints.

    Returns only the fields needed to render a table row.
    """

    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    class Meta:
        model = Patient
        fields = (
            "id",
            "full_name",
            "medical_record_number",
            "birth_date",
            "sex",
            "vital_status",
            "organization",
            "organization_name",
            "created_at",
        )
        read_only_fields = fields


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
            "vital_status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_age(self, obj: Patient) -> int | None:
        """Compute age in full years from birth_date."""
        from datetime import date

        if not obj.birth_date:
            return None
        today = date.today()
        years = today.year - obj.birth_date.year
        if (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day):
            years -= 1
        return years

    def validate_organization(self, value: Organization) -> Organization:
        """Ensure the user can assign patients only to their own organization.

        Superusers may assign to any organization.
        """
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

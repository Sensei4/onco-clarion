"""Serializers for diagnostic reference data (departments, methods)."""

from rest_framework import serializers

from .models import DiagnosticDepartment, DiagnosticMethod


class DiagnosticMethodSerializer(serializers.ModelSerializer):
    """Read-only serializer for diagnostic methods."""

    class Meta:
        model = DiagnosticMethod
        fields = (
            "id",
            "department",
            "code",
            "name",
            "is_active",
        )
        read_only_fields = fields


class DiagnosticDepartmentSerializer(serializers.ModelSerializer):
    """Read-only serializer for diagnostic departments.

    Includes a nested list of active methods for the department.
    """

    methods = serializers.SerializerMethodField()

    class Meta:
        model = DiagnosticDepartment
        fields = (
            "id",
            "name",
            "category",
            "is_active",
            "methods",
        )
        read_only_fields = fields

    def get_methods(self, obj: DiagnosticDepartment):
        """Return only active methods, ordered by name."""
        methods = obj.methods.filter(is_active=True).order_by("name")
        return DiagnosticMethodSerializer(methods, many=True).data

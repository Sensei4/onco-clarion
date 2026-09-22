from rest_framework import serializers

from .models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    """Read-only serializer for audit events."""

    user_name = serializers.CharField(
        source="user.username",
        read_only=True,
        default=None,
    )
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
        default=None,
    )

    class Meta:
        model = AuditEvent
        fields = (
            "id",
            "user",
            "user_name",
            "action",
            "entity_type",
            "entity_id",
            "entity_repr",
            "organization",
            "organization_name",
            "timestamp",
            "ip_address",
            "user_agent",
            "request_method",
            "request_path",
        )
        read_only_fields = fields

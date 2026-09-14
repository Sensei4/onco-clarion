from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
        default=None,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "full_name",
            "role",
            "organization",
            "organization_name",
            "is_active",
            "is_staff",
            "is_superuser",
        )
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})
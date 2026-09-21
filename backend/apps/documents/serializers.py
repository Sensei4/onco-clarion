from rest_framework import serializers

from .models import Document


class DocumentListSerializer(serializers.ModelSerializer):
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
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.username",
        read_only=True,
    )
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            "id",
            "case",
            "case_diagnosis",
            "patient_name",
            "patient_mrn",
            "event",
            "referral",
            "organization",
            "type",
            "title",
            "original_filename",
            "content_type",
            "file_size",
            "file_url",
            "uploaded_by",
            "uploaded_by_name",
            "uploaded_at",
        )
        read_only_fields = fields

    def get_file_url(self, obj: Document) -> str | None:
        if not obj.file:
            return None
        request = self.context.get("request")
        url = obj.file.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class DocumentDetailSerializer(serializers.ModelSerializer):
    """Full serializer for retrieve, upload, and update."""

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
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.username",
        read_only=True,
    )
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            "id",
            "case",
            "case_diagnosis",
            "patient_name",
            "patient_mrn",
            "event",
            "referral",
            "organization",
            "type",
            "title",
            "file",
            "file_url",
            "original_filename",
            "content_type",
            "file_size",
            "uploaded_by",
            "uploaded_by_name",
            "uploaded_at",
        )
        read_only_fields = (
            "id",
            "original_filename",
            "content_type",
            "file_size",
            "uploaded_by",
            "uploaded_at",
        )

    def get_file_url(self, obj: Document) -> str | None:
        if not obj.file:
            return None
        request = self.context.get("request")
        url = obj.file.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url

    def validate_case(self, value):
        """Ensure the user can only upload to cases in their org."""
        request = self.context.get("request")
        if request is None:
            return value
        user = request.user
        if user.is_superuser:
            return value
        if value.organization_id != user.organization_id:
            raise serializers.ValidationError(
                "You can only attach documents to cases in your organization."
            )
        return value

    def create(self, validated_data):
        """Fill content_type and original_filename from the uploaded file."""
        request = self.context.get("request")
        if request is not None and "uploaded_by" not in validated_data:
            validated_data["uploaded_by"] = request.user

        file = validated_data.get("file")
        if file is not None:
            # original_filename will be set in model.save if empty
            pass

        instance = super().create(validated_data)

        # Try to extract content_type from the uploaded file
        if file is not None and hasattr(file, "content_type"):
            instance.content_type = file.content_type or ""
            instance.save(update_fields=["content_type"])

        return instance


class DocumentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating document metadata (not the file)."""

    class Meta:
        model = Document
        fields = (
            "id",
            "type",
            "title",
            "event",
            "referral",
        )
        read_only_fields = ("id",)

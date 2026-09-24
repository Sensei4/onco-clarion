from rest_framework import serializers

from .models import FoundationEntity, MmsEntity


class MmsEntityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for search results and autocomplete."""

    class Meta:
        model = MmsEntity
        fields = (
            "uri",
            "the_code",
            "title",
            "chapter",
            "is_leaf",
            "synonyms",
            "foundation_uri",
        )
        read_only_fields = fields


class MmsEntityDetailSerializer(serializers.ModelSerializer):
    """Full serializer for a single MMS entity."""

    class Meta:
        model = MmsEntity
        fields = (
            "uri",
            "the_code",
            "title",
            "chapter",
            "is_leaf",
            "is_residual_unspecified",
            "is_residual_other",
            "parent_uris",
            "child_uris",
            "synonyms",
            "foundation_uri",
            "last_synced_at",
        )
        read_only_fields = fields


class FoundationEntitySerializer(serializers.ModelSerializer):
    """Foundation entity serializer."""

    class Meta:
        model = FoundationEntity
        fields = (
            "uri",
            "title",
            "definition",
            "long_definition",
            "synonyms",
            "parent_uris",
            "child_uris",
            "exclusions",
            "browser_url",
            "chapter",
            "last_synced_at",
        )
        read_only_fields = fields


class ChapterSerializer(serializers.Serializer):
    """Chapter summary for filter dropdowns."""

    chapter = serializers.CharField()
    count = serializers.IntegerField()

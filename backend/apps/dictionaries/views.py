from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import FoundationEntity, MmsEntity
from .serializers import (
    ChapterSerializer,
    FoundationEntitySerializer,
    MmsEntityDetailSerializer,
    MmsEntityListSerializer,
)


class Icd11ViewSet(viewsets.GenericViewSet):
    """Read-only access to the locally synced ICD-11 reference data.

    All endpoints are read-only and accessible to any authenticated user.
    Data is served from the local database (no calls to ICD-API at runtime).
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """Search MMS entities by code, title, or synonyms.

        Query params:
          - q: search term (required, min 2 chars)
          - chapter: filter by chapter (optional)
          - page, page_size: pagination

        The query is split into words. All words must match (AND).
        Each word can match the code, title, or synonyms.
        """
        q = (request.query_params.get("q") or "").strip()
        if len(q) < 2:
            return Response(
                {"detail": "Query must be at least 2 characters."},
                status=400,
            )

        qs = MmsEntity.objects.all()

        chapter = request.query_params.get("chapter")
        if chapter:
            qs = qs.filter(chapter=chapter)

        # Split query into words; AND between them, OR within each word
        terms = [t for t in q.split() if t]
        for term in terms:
            qs = qs.filter(
                Q(the_code__icontains=term) | Q(title__icontains=term) | Q(synonyms__icontains=term)
            )
        qs = qs.order_by("the_code")

        # Pagination (use DRF's default paginator)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = MmsEntityListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MmsEntityListSerializer(qs[:100], many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"entities/(?P<uri_id>[^/]+(?:/[^/]+)*)",
    )
    def entity_detail(self, request, uri_id=None):
        """Get a single MMS entity by its URI suffix or full URI.

        Examples:
          /api/dictionaries/icd11/entities/1047754165/unspecified/
          /api/dictionaries/icd11/entities/1435254666/
        """
        # Try exact match on the URI suffix first
        uri_suffix = uri_id or ""
        candidates = MmsEntity.objects.filter(uri__endswith=f"/{uri_suffix}")

        if not candidates.exists():
            # Try with full URI
            candidates = MmsEntity.objects.filter(uri=uri_suffix)

        entity = candidates.first()
        if entity is None:
            return Response(
                {"detail": "Entity not found."},
                status=404,
            )

        serializer = MmsEntityDetailSerializer(entity)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="chapters")
    def chapters(self, request):
        """List available chapters with entity counts."""
        qs = (
            MmsEntity.objects.exclude(chapter="")
            .values("chapter")
            .annotate(count=Count("id"))
            .order_by("chapter")
        )
        serializer = ChapterSerializer(qs, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"foundation/(?P<uri_id>[^/]+(?:/[^/]+)*)",
    )
    def foundation_detail(self, request, uri_id=None):
        """Get a foundation entity by its URI suffix or full URI."""
        uri_suffix = uri_id or ""
        candidates = FoundationEntity.objects.filter(uri__endswith=f"/{uri_suffix}")
        if not candidates.exists():
            candidates = FoundationEntity.objects.filter(uri=uri_suffix)

        entity = candidates.first()
        if entity is None:
            return Response(
                {"detail": "Foundation entity not found."},
                status=404,
            )
        serializer = FoundationEntitySerializer(entity)
        return Response(serializer.data)

from django.db.models import Q, QuerySet
from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Document
from .serializers import (
    DocumentDetailSerializer,
    DocumentListSerializer,
    DocumentUpdateSerializer,
)


class DocumentViewSet(viewsets.ModelViewSet):
    """CRUD for case documents, scoped to the current user's organization.

    Upload uses multipart/form-data.
    Files can be downloaded via /api/documents/{id}/download/.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self) -> QuerySet[Document]:
        user = self.request.user
        qs = Document.objects.select_related(
            "case",
            "case__patient",
            "event",
            "referral",
            "organization",
            "uploaded_by",
        ).order_by("-uploaded_at")

        if not user.is_superuser:
            if user.organization_id is None:
                return qs.none()
            qs = qs.filter(organization_id=user.organization_id)

        case_id = self.request.query_params.get("case")
        if case_id:
            qs = qs.filter(case_id=case_id)

        event_id = self.request.query_params.get("event")
        if event_id:
            qs = qs.filter(event_id=event_id)

        referral_id = self.request.query_params.get("referral")
        if referral_id:
            qs = qs.filter(referral_id=referral_id)

        type_filter = self.request.query_params.get("type")
        if type_filter:
            qs = qs.filter(type=type_filter)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(original_filename__icontains=search)
                | Q(case__patient__full_name__icontains=search)
                | Q(case__patient__medical_record_number__icontains=search)
            )

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return DocumentListSerializer
        if self.action in ("update", "partial_update"):
            return DocumentUpdateSerializer
        return DocumentDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        """Serve the file with proper permission checks."""
        document = self.get_object()
        if not document.file:
            return Response(
                {"detail": "File is missing."},
                status=status.HTTP_404_NOT_FOUND,
            )
        response = FileResponse(
            document.file.open("rb"),
            as_attachment=True,
            filename=document.original_filename or "download",
        )
        if document.content_type:
            response["Content-Type"] = document.content_type
        return response

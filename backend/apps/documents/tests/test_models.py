import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.documents.models import Document


@pytest.mark.django_db
class TestDocumentModel:
    def test_str_with_title(self, document):
        assert str(document) == "Histology report"

    def test_str_falls_back_to_filename(self, db, case, organization, doctor):
        doc = Document.objects.create(
            case=case,
            organization=organization,
            type=Document.Type.OTHER,
            file=SimpleUploadedFile(
                "scan.pdf",
                b"%PDF-1.4",
                content_type="application/pdf",
            ),
            uploaded_by=doctor,
        )
        # Django renames the physical file if a collision occurs
        # (e.g. "scan_XXXXX.pdf"), but original_filename is preserved.
        assert "scan" in str(doc)
        assert doc.original_filename == "scan.pdf"

    def test_original_filename_auto_filled(self, document):
        assert document.original_filename == "histology.pdf"

    def test_file_size_auto_filled(self, document):
        assert document.file_size is not None
        assert document.file_size > 0

    def test_default_type_is_other(self, db, case, organization, doctor):
        doc = Document.objects.create(
            case=case,
            organization=organization,
            file=SimpleUploadedFile("x.pdf", b"%PDF-1.4"),
            uploaded_by=doctor,
        )
        assert doc.type == "other"

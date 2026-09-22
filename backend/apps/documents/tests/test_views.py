import pytest
from rest_framework.test import APIClient

from apps.documents.models import Document
from apps.documents.tests.conftest import make_pdf


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestDocumentList:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/documents/")
        assert response.status_code == 403

    def test_doctor_sees_only_own_organization(self, api_client, doctor, document, other_document):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/documents/")
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_superuser_sees_all(self, api_client, superuser, document, other_document):
        api_client.force_authenticate(user=superuser)
        response = api_client.get("/api/documents/")
        assert response.json()["count"] == 2

    def test_file_url_is_relative(self, api_client, doctor, document):
        """file_url is relative (/media/...) so it works through
        the Vite proxy in dev and through Caddy in prod.
        """
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/documents/")
        file_url = response.json()["results"][0]["file_url"]
        assert file_url.startswith("/media/")

    def test_filter_by_case(self, api_client, doctor, case, document):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/documents/?case={case.id}")
        assert response.json()["count"] == 1

    def test_filter_by_type(self, api_client, doctor, document):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/documents/?type=histology")
        assert response.json()["count"] == 1

    def test_search_by_title(self, api_client, doctor, document):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/documents/?search=Histology")
        assert response.json()["count"] == 1

    def test_search_no_match(self, api_client, doctor, document):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/documents/?search=ZZZZZ")
        assert response.json()["count"] == 0


@pytest.mark.django_db
class TestDocumentRetrieve:
    def test_doctor_can_retrieve_own(self, api_client, doctor, document):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/documents/{document.id}/")
        assert response.status_code == 200
        assert response.json()["title"] == "Histology report"

    def test_doctor_cannot_retrieve_foreign(self, api_client, doctor, other_document):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/documents/{other_document.id}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestDocumentUpload:
    def test_doctor_can_upload(self, api_client, doctor, case, organization):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/documents/",
            {
                "case": case.id,
                "organization": organization.id,
                "type": "analysis",
                "title": "Blood test",
                "file": make_pdf("blood.pdf"),
            },
            format="multipart",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "analysis"
        assert data["original_filename"] == "blood.pdf"
        assert data["file_size"] > 0
        assert data["uploaded_by"] == doctor.id

    def test_uploaded_by_cannot_be_spoofed(self, api_client, doctor, superuser, case, organization):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/documents/",
            {
                "case": case.id,
                "organization": organization.id,
                "type": "other",
                "file": make_pdf("x.pdf"),
                "uploaded_by": superuser.id,
            },
            format="multipart",
        )
        assert response.status_code == 201
        doc = Document.objects.get(id=response.json()["id"])
        assert doc.uploaded_by == doctor

    def test_doctor_cannot_upload_to_foreign_case(
        self, api_client, doctor, other_case, organization
    ):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/documents/",
            {
                "case": other_case.id,
                "organization": organization.id,
                "type": "other",
                "file": make_pdf("x.pdf"),
            },
            format="multipart",
        )
        assert response.status_code == 400
        assert "case" in response.json()


@pytest.mark.django_db
class TestDocumentDownload:
    def test_download_returns_file(self, api_client, doctor, document):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/documents/{document.id}/download/")
        assert response.status_code == 200
        assert "attachment" in response["Content-Disposition"]

    def test_doctor_cannot_download_foreign(self, api_client, doctor, other_document):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/documents/{other_document.id}/download/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestDocumentUpdate:
    def test_doctor_can_update_metadata(self, api_client, doctor, document):
        api_client.force_authenticate(user=doctor)
        response = api_client.patch(
            f"/api/documents/{document.id}/",
            {"title": "Updated title"},
            format="json",
        )
        assert response.status_code == 200
        document.refresh_from_db()
        assert document.title == "Updated title"


@pytest.mark.django_db
class TestDocumentDelete:
    def test_doctor_can_delete_own(self, api_client, doctor, document):
        api_client.force_authenticate(user=doctor)
        response = api_client.delete(f"/api/documents/{document.id}/")
        assert response.status_code == 204
        assert not Document.objects.filter(id=document.id).exists()

    def test_doctor_cannot_delete_foreign(self, api_client, doctor, other_document):
        api_client.force_authenticate(user=doctor)
        response = api_client.delete(f"/api/documents/{other_document.id}/")
        assert response.status_code == 404

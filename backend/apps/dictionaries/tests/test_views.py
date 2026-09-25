import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestIcd11Search:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/dictionaries/icd11/search/?q=breast")
        assert response.status_code == 403

    def test_short_query_returns_400(self, api_client, doctor):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/dictionaries/icd11/search/?q=a")
        assert response.status_code == 400
        assert "at least 2 characters" in response.json()["detail"]

    def test_search_by_code(self, api_client, doctor, mms_breast, mms_ductal):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/dictionaries/icd11/search/?q=2C61")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["the_code"] == "2C61.0"

    def test_search_by_title_word(self, api_client, doctor, mms_breast, mms_ductal):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/dictionaries/icd11/search/?q=invasive")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["the_code"] == "2C61.0"

    def test_search_by_synonym(self, api_client, doctor, mms_breast, mms_ductal):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/dictionaries/icd11/search/?q=breast+cancer")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        codes = [r["the_code"] for r in data["results"]]
        assert "2C6Z" in codes

    def test_multi_word_and(self, api_client, doctor, mms_breast, mms_ductal):
        """'ductal breast' should match only entities with both words."""
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/dictionaries/icd11/search/?q=ductal+breast")
        assert response.status_code == 200
        data = response.json()
        codes = [r["the_code"] for r in data["results"]]
        assert "2C61.0" in codes
        assert "2C6Z" not in codes

    def test_filter_by_chapter(self, api_client, doctor, mms_breast):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/dictionaries/icd11/search/?q=breast&chapter=02")
        assert response.status_code == 200
        assert response.json()["count"] >= 1

    def test_no_results(self, api_client, doctor, mms_breast):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/dictionaries/icd11/search/?q=zzzzzzzzz")
        assert response.status_code == 200
        assert response.json()["count"] == 0


@pytest.mark.django_db
class TestIcd11EntityDetail:
    def test_get_by_uri_suffix(self, api_client, doctor, mms_breast):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/dictionaries/icd11/entities/1047754165/unspecified/")
        assert response.status_code == 200
        data = response.json()
        assert data["the_code"] == "2C6Z"
        assert data["title"] == "Malignant neoplasms of breast, unspecified"
        assert "breast cancer" in data["synonyms"]

    def test_get_by_numeric_id(self, api_client, doctor, mms_ductal):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/dictionaries/icd11/entities/175963120/")
        assert response.status_code == 200
        assert response.json()["the_code"] == "2C61.0"

    def test_not_found(self, api_client, doctor):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/dictionaries/icd11/entities/999999999/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestIcd11Chapters:
    def test_lists_chapters_with_counts(self, api_client, doctor, mms_breast, mms_ductal):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/dictionaries/icd11/chapters/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["chapter"] == "02"
        assert data[0]["count"] == 2

    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/dictionaries/icd11/chapters/")
        assert response.status_code == 403

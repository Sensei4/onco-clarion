import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Organization


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestOrganizationList:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/organizations/")
        assert response.status_code == 403

    def test_doctor_can_list(self, api_client, doctor_user, organization):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.get("/api/organizations/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["name"] == organization.name


@pytest.mark.django_db
class TestOrganizationCreate:
    def test_admin_can_create(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            "/api/organizations/",
            {"name": "New Center", "country": "KZ"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "New Center"
        assert Organization.objects.filter(name="New Center").exists()

    def test_doctor_cannot_create(self, api_client, doctor_user):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.post(
            "/api/organizations/",
            {"name": "Forbidden", "country": "XX"},
            format="json",
        )
        assert response.status_code == 403

    def test_superuser_can_create(self, api_client, superuser):
        api_client.force_authenticate(user=superuser)
        response = api_client.post(
            "/api/organizations/",
            {"name": "Super Org", "country": "US"},
            format="json",
        )
        assert response.status_code == 201


@pytest.mark.django_db
class TestOrganizationUpdate:
    def test_admin_can_update(self, api_client, admin_user, organization):
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(
            f"/api/organizations/{organization.id}/",
            {"name": "Updated Name"},
            format="json",
        )
        assert response.status_code == 200
        organization.refresh_from_db()
        assert organization.name == "Updated Name"

    def test_doctor_cannot_update(self, api_client, doctor_user, organization):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.patch(
            f"/api/organizations/{organization.id}/",
            {"name": "Hacked"},
            format="json",
        )
        assert response.status_code == 403

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestLogin:
    def test_login_with_valid_credentials(self, api_client, doctor_user):
        response = api_client.post(
            "/api/auth/login/",
            {"username": "doctor1", "password": "strong-pass-12345"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["username"] == "doctor1"
        assert response.json()["role"] == "doctor"

    def test_login_with_invalid_password(self, api_client, doctor_user):
        response = api_client.post(
            "/api/auth/login/",
            {"username": "doctor1", "password": "wrong"},
            format="json",
        )
        assert response.status_code == 401

    def test_login_with_unknown_user(self, api_client):
        response = api_client.post(
            "/api/auth/login/",
            {"username": "ghost", "password": "whatever"},
            format="json",
        )
        assert response.status_code == 401

    def test_login_with_inactive_user(self, api_client, db, organization):
        User.objects.create_user(
            username="inactive",
            password="strong-pass-12345",
            organization=organization,
            is_active=False,
        )
        response = api_client.post(
            "/api/auth/login/",
            {"username": "inactive", "password": "strong-pass-12345"},
            format="json",
        )
        # authenticate() returns None for inactive users
        assert response.status_code == 401


@pytest.mark.django_db
class TestMe:
    def test_me_requires_authentication(self, api_client):
        response = api_client.get("/api/auth/me/")
        assert response.status_code == 403

    def test_me_returns_current_user(self, api_client, doctor_user):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.get("/api/auth/me/")
        assert response.status_code == 200
        assert response.json()["username"] == "doctor1"
        assert response.json()["role"] == "doctor"


@pytest.mark.django_db
class TestLogout:
    def test_logout(self, api_client, doctor_user):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.post("/api/auth/logout/")
        assert response.status_code == 204

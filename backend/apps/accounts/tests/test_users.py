import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestUserList:
    def test_admin_can_list(self, api_client, admin_user, doctor_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/users/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        usernames = {u["username"] for u in data["results"]}
        assert usernames == {"admin1", "doctor1"}

    def test_doctor_cannot_list(self, api_client, doctor_user, admin_user):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.get("/api/users/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestUserCreate:
    def test_admin_can_create_with_password(self, api_client, admin_user, organization):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            "/api/users/",
            {
                "username": "newdoctor",
                "email": "new@example.com",
                "full_name": "New Doctor",
                "role": "doctor",
                "organization": organization.id,
                "is_active": True,
                "password": "another-strong-pass-1",
            },
            format="json",
        )
        assert response.status_code == 201
        user = User.objects.get(username="newdoctor")
        assert user.check_password("another-strong-pass-1")
        assert user.full_name == "New Doctor"

    def test_created_user_without_password_cannot_login(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            "/api/users/",
            {
                "username": "nopassword",
                "role": "doctor",
                "is_active": True,
            },
            format="json",
        )
        assert response.status_code == 201
        user = User.objects.get(username="nopassword")
        assert not user.has_usable_password()

    def test_password_not_returned_in_response(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            "/api/users/",
            {
                "username": "secret",
                "role": "doctor",
                "password": "another-strong-pass-2",
            },
            format="json",
        )
        assert response.status_code == 201
        assert "password" not in response.json()

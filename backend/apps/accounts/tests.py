from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class AuthEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="doctor1",
            password="strong-pass-12345",
            full_name="Doctor One",
            role="doctor",
        )

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "doctor1", "password": "strong-pass-12345"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "doctor1")

    def test_login_with_invalid_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "doctor1", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_me_requires_authentication(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 403)

    def test_me_returns_current_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "doctor1")

    def test_logout(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, 204)

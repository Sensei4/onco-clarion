import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestCompleteAction:
    def test_complete_ordered_referral(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            f"/api/referrals/{referral.id}/complete/",
            {"result_text": "Normal"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["result_text"] == "Normal"
        assert data["result_received_at"] is not None
        assert data["completed_by"] == doctor.id

    def test_complete_without_result_text(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            f"/api/referrals/{referral.id}/complete/",
            {},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["result_text"] == ""

    def test_cannot_complete_twice(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        api_client.post(
            f"/api/referrals/{referral.id}/complete/",
            {"result_text": "First"},
            format="json",
        )
        response = api_client.post(
            f"/api/referrals/{referral.id}/complete/",
            {"result_text": "Second"},
            format="json",
        )
        assert response.status_code == 409

    def test_cannot_complete_cancelled(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        api_client.post(f"/api/referrals/{referral.id}/cancel/", {}, format="json")
        response = api_client.post(
            f"/api/referrals/{referral.id}/complete/",
            {},
            format="json",
        )
        assert response.status_code == 409


@pytest.mark.django_db
class TestCancelAction:
    def test_cancel_ordered_referral(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            f"/api/referrals/{referral.id}/cancel/",
            {"reason": "Patient refused"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    def test_cancel_adds_reason_to_notes(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        api_client.post(
            f"/api/referrals/{referral.id}/cancel/",
            {"reason": "Patient refused"},
            format="json",
        )
        referral.refresh_from_db()
        assert "Cancelled: Patient refused" in referral.notes

    def test_cannot_cancel_completed(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        api_client.post(
            f"/api/referrals/{referral.id}/complete/",
            {},
            format="json",
        )
        response = api_client.post(
            f"/api/referrals/{referral.id}/cancel/",
            {},
            format="json",
        )
        assert response.status_code == 409


@pytest.mark.django_db
class TestReopenAction:
    def test_reopen_completed(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        api_client.post(
            f"/api/referrals/{referral.id}/complete/",
            {"result_text": "Old result"},
            format="json",
        )
        response = api_client.post(
            f"/api/referrals/{referral.id}/reopen/",
            {},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ordered"
        assert data["result_text"] == ""
        assert data["completed_by"] is None

    def test_cannot_reopen_ordered(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            f"/api/referrals/{referral.id}/reopen/",
            {},
            format="json",
        )
        assert response.status_code == 409


@pytest.mark.django_db
class TestActionMultiTenancy:
    def test_doctor_cannot_complete_foreign_referral(self, api_client, doctor, other_referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            f"/api/referrals/{other_referral.id}/complete/",
            {"result_text": "Hack"},
            format="json",
        )
        assert response.status_code == 404

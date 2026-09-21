import pytest
from rest_framework.test import APIClient

from apps.referrals.models import Referral


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestReferralList:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/referrals/")
        assert response.status_code == 403

    def test_doctor_sees_only_own_organization(self, api_client, doctor, referral, other_referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/referrals/")
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_superuser_sees_all(self, api_client, superuser, referral, other_referral):
        api_client.force_authenticate(user=superuser)
        response = api_client.get("/api/referrals/")
        assert response.json()["count"] == 2

    def test_filter_by_case(self, api_client, doctor, case, referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/referrals/?case={case.id}")
        assert response.json()["count"] == 1

    def test_filter_by_status(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/referrals/?status=ordered")
        assert response.json()["count"] == 1

    def test_filter_by_type(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/referrals/?type=imaging")
        assert response.json()["count"] == 1

    def test_search_by_title(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/referrals/?search=CT")
        assert response.json()["count"] == 1

    def test_search_no_match(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/referrals/?search=ZZZZZ")
        assert response.json()["count"] == 0


@pytest.mark.django_db
class TestReferralRetrieve:
    def test_doctor_can_retrieve_own(self, api_client, doctor, referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/referrals/{referral.id}/")
        assert response.status_code == 200
        assert response.json()["title"] == "CT chest with contrast"

    def test_doctor_cannot_retrieve_foreign(self, api_client, doctor, other_referral):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/referrals/{other_referral.id}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestReferralCreate:
    def test_doctor_can_create(self, api_client, doctor, case, organization):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/referrals/",
            {
                "case": case.id,
                "organization": organization.id,
                "type": "histology",
                "title": "Biopsy",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["status"] == "ordered"
        assert response.json()["ordered_by"] == doctor.id

    def test_ordered_by_cannot_be_spoofed(self, api_client, doctor, superuser, case, organization):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/referrals/",
            {
                "case": case.id,
                "organization": organization.id,
                "type": "lab",
                "ordered_by": superuser.id,  # should be ignored
            },
            format="json",
        )
        assert response.status_code == 201
        ref = Referral.objects.get(id=response.json()["id"])
        assert ref.ordered_by == doctor

    def test_doctor_cannot_create_for_foreign_case(
        self, api_client, doctor, other_case, organization
    ):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/referrals/",
            {
                "case": other_case.id,
                "organization": organization.id,
                "type": "lab",
            },
            format="json",
        )
        assert response.status_code == 400
        assert "case" in response.json()

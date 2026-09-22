import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestAuditPermissions:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/audit/")
        assert response.status_code == 403

    def test_doctor_cannot_access(self, api_client, doctor, event_in_org_a):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/audit/")
        assert response.status_code == 403

    def test_admin_can_access(self, api_client, admin_user, event_in_org_a):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/audit/")
        assert response.status_code == 200

    def test_superuser_can_access(self, api_client, superuser, event_in_org_a, event_in_org_b):
        api_client.force_authenticate(user=superuser)
        response = api_client.get("/api/audit/")
        assert response.status_code == 200
        assert response.json()["count"] == 2


@pytest.mark.django_db
class TestAuditMultiTenancy:
    def test_admin_sees_only_own_org(self, api_client, admin_user, event_in_org_a, event_in_org_b):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/audit/")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["entity_repr"] == "Ivan Petrov (MRN-0001)"

    def test_superuser_sees_all_orgs(self, api_client, superuser, event_in_org_a, event_in_org_b):
        api_client.force_authenticate(user=superuser)
        response = api_client.get("/api/audit/")
        assert response.json()["count"] == 2


@pytest.mark.django_db
class TestAuditFilters:
    def test_filter_by_action(
        self,
        api_client,
        admin_user,
        event_in_org_a,
        download_event,
    ):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/audit/?action=download")
        assert response.json()["count"] == 1
        assert response.json()["results"][0]["action"] == "download"

    def test_filter_by_entity_type(self, api_client, admin_user, event_in_org_a, download_event):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/audit/?entity_type=Document")
        assert response.json()["count"] == 1

    def test_filter_by_entity_id(self, api_client, admin_user, event_in_org_a):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/audit/?entity_id=1")
        assert response.json()["count"] == 1

    def test_search_by_repr(self, api_client, admin_user, event_in_org_a):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/audit/?search=Ivan")
        assert response.json()["count"] == 1

    def test_search_no_match(self, api_client, admin_user, event_in_org_a):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/audit/?search=ZZZZZ")
        assert response.json()["count"] == 0


@pytest.mark.django_db
class TestAuditRetrieve:
    def test_admin_can_retrieve_own_org_event(self, api_client, admin_user, event_in_org_a):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f"/api/audit/{event_in_org_a.id}/")
        assert response.status_code == 200

    def test_admin_cannot_retrieve_foreign_event(self, api_client, admin_user, event_in_org_b):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f"/api/audit/{event_in_org_b.id}/")
        assert response.status_code == 404

    def test_audit_events_cannot_be_created_via_api(self, api_client, admin_user):
        """POST to /api/audit/ should return 405."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            "/api/audit/",
            {"action": "view", "entity_type": "Patient"},
            format="json",
        )
        assert response.status_code == 405

    def test_audit_events_cannot_be_deleted_via_api(self, api_client, admin_user, event_in_org_a):
        """DELETE on /api/audit/{id}/ should return 405."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.delete(f"/api/audit/{event_in_org_a.id}/")
        assert response.status_code == 405

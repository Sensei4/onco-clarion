import pytest
from rest_framework.test import APIClient

from apps.cases.models import CancerCase, StatusTransition


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestTransitionEndpoint:
    def test_valid_transition_changes_status(self, api_client, doctor, case):
        """POST /transition/ with valid action changes status."""
        api_client.force_authenticate(user=doctor)
        assert case.status == "new"

        response = api_client.post(
            f"/api/cases/{case.id}/transition/",
            {"action": "start_diagnostics", "reason": "Initial workup"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["status"] == "diagnostic"

        fresh = CancerCase.objects.get(pk=case.pk)
        assert fresh.status == "diagnostic"

    def test_invalid_transition_returns_409(self, api_client, doctor, case):
        """POST /transition/ with action not allowed from current status → 409."""
        api_client.force_authenticate(user=doctor)

        response = api_client.post(
            f"/api/cases/{case.id}/transition/",
            {"action": "mark_remission", "reason": "nope"},
            format="json",
        )
        assert response.status_code == 409
        assert "detail" in response.json()

        # Status did not change
        fresh = CancerCase.objects.get(pk=case.pk)
        assert fresh.status == "new"

    def test_unknown_action_returns_400(self, api_client, doctor, case):
        """POST /transition/ with action that doesn't exist → 400."""
        api_client.force_authenticate(user=doctor)

        response = api_client.post(
            f"/api/cases/{case.id}/transition/",
            {"action": "fly_to_the_moon", "reason": "?"},
            format="json",
        )
        assert response.status_code == 400
        assert "action" in response.json()

    def test_non_transition_method_returns_400(self, api_client, doctor, case):
        """POST /transition/ with a real method that isn't a transition → 400."""
        api_client.force_authenticate(user=doctor)

        response = api_client.post(
            f"/api/cases/{case.id}/transition/",
            {"action": "delete", "reason": "hack"},
            format="json",
        )
        assert response.status_code == 400
        assert "action" in response.json()

    def test_requires_authentication(self, api_client, case):
        response = api_client.post(
            f"/api/cases/{case.id}/transition/",
            {"action": "start_diagnostics"},
            format="json",
        )
        assert response.status_code == 403

    def test_doctor_cannot_transition_foreign_case(self, api_client, doctor, other_case):
        """Multi-tenancy: doctor cannot transition a case in another org."""
        api_client.force_authenticate(user=doctor)

        response = api_client.post(
            f"/api/cases/{other_case.id}/transition/",
            {"action": "start_diagnostics", "reason": "test"},
            format="json",
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestTransitionAudit:
    def test_transition_creates_audit_record(self, api_client, doctor, case):
        """A successful transition creates exactly one StatusTransition."""
        api_client.force_authenticate(user=doctor)

        assert StatusTransition.objects.filter(case=case).count() == 0

        api_client.post(
            f"/api/cases/{case.id}/transition/",
            {"action": "start_diagnostics", "reason": "Initial workup"},
            format="json",
        )

        assert StatusTransition.objects.filter(case=case).count() == 1
        transition = StatusTransition.objects.get(case=case)
        assert transition.from_status == "new"
        assert transition.to_status == "diagnostic"
        assert transition.transitioned_by == doctor
        assert transition.reason == "Initial workup"

    def test_failed_transition_does_not_create_audit(self, api_client, doctor, case):
        """A blocked transition must not create an audit record."""
        api_client.force_authenticate(user=doctor)

        api_client.post(
            f"/api/cases/{case.id}/transition/",
            {"action": "mark_remission", "reason": "nope"},
            format="json",
        )

        assert StatusTransition.objects.filter(case=case).count() == 0

    def test_transition_reason_can_be_empty(self, api_client, doctor, case):
        """reason is optional."""
        api_client.force_authenticate(user=doctor)

        response = api_client.post(
            f"/api/cases/{case.id}/transition/",
            {"action": "start_diagnostics"},
            format="json",
        )
        assert response.status_code == 200

        transition = StatusTransition.objects.get(case=case)
        assert transition.reason == ""


@pytest.mark.django_db
class TestTransitionListEndpoint:
    def test_returns_empty_for_case_without_transitions(self, api_client, doctor, case):
        api_client.force_authenticate(user=doctor)

        response = api_client.get(f"/api/cases/{case.id}/transitions/")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_transitions_in_reverse_chronological_order(self, api_client, doctor, case):
        api_client.force_authenticate(user=doctor)

        # Two transitions
        api_client.post(
            f"/api/cases/{case.id}/transition/",
            {"action": "start_diagnostics", "reason": "first"},
            format="json",
        )
        api_client.post(
            f"/api/cases/{case.id}/transition/",
            {"action": "schedule_consilium", "reason": "second"},
            format="json",
        )

        response = api_client.get(f"/api/cases/{case.id}/transitions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Newest first
        assert data[0]["from_status"] == "diagnostic"
        assert data[0]["to_status"] == "consilium"
        assert data[0]["reason"] == "second"
        assert data[1]["from_status"] == "new"
        assert data[1]["to_status"] == "diagnostic"
        assert data[1]["reason"] == "first"

    def test_doctor_cannot_list_foreign_case_transitions(self, api_client, doctor, other_case):
        api_client.force_authenticate(user=doctor)

        response = api_client.get(f"/api/cases/{other_case.id}/transitions/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestFullLifecycle:
    def test_forward_cycle(self, api_client, doctor, case):
        """Run the full forward cycle and check final status and audit."""
        api_client.force_authenticate(user=doctor)

        actions = [
            "start_diagnostics",
            "schedule_consilium",
            "approve_hospitalization",
            "admit_to_hospital",
            "complete_treatment",
            "mark_remission",
        ]
        for action in actions:
            response = api_client.post(
                f"/api/cases/{case.id}/transition/",
                {"action": action, "reason": action},
                format="json",
            )
            assert response.status_code == 200, f"{action} failed: {response.json()}"

        fresh = CancerCase.objects.get(pk=case.pk)
        assert fresh.status == "remission"
        assert StatusTransition.objects.filter(case=case).count() == 6

    def test_relapse_cycle(self, api_client, doctor, case):
        """Run forward cycle, then relapse, then back to consilium."""
        api_client.force_authenticate(user=doctor)

        forward = [
            "start_diagnostics",
            "schedule_consilium",
            "approve_hospitalization",
            "admit_to_hospital",
            "complete_treatment",
            "mark_remission",
        ]
        for action in forward:
            api_client.post(
                f"/api/cases/{case.id}/transition/",
                {"action": action},
                format="json",
            )

        # Relapse
        response = api_client.post(
            f"/api/cases/{case.id}/transition/",
            {"action": "mark_relapse", "reason": "Recurrence"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["status"] == "relapse"

        # Back to consilium
        response = api_client.post(
            f"/api/cases/{case.id}/transition/",
            {"action": "reschedule_consilium", "reason": "New plan"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["status"] == "consilium"

        assert StatusTransition.objects.filter(case=case).count() == 8

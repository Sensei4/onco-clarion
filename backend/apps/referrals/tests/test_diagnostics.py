import pytest
from rest_framework.test import APIClient

from apps.referrals.models import (
    DiagnosticDepartment,
    DiagnosticMethod,
    Referral,
)


@pytest.fixture
def api_client():
    return APIClient()


# ---------------------------------------------------------------------------
# Departments and methods API
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDiagnosticDepartmentsAPI:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/referrals/departments/")
        assert response.status_code == 403

    def test_list_returns_departments(self, api_client, doctor, department):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/referrals/departments/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["name"] == "Clinical laboratory"
        assert data["results"][0]["category"] == "laboratory"

    def test_nested_methods_included(self, api_client, doctor, department, method):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/referrals/departments/")
        dept = response.json()["results"][0]
        assert len(dept["methods"]) == 1
        assert dept["methods"][0]["code"] == "CBC"

    def test_multi_tenancy(
        self,
        api_client,
        doctor,
        department,
        other_department,
    ):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/referrals/departments/")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["name"] == "Clinical laboratory"

    def test_filter_by_category(self, api_client, doctor, department, organization):
        # Second department with different category
        DiagnosticDepartment.objects.create(
            organization=organization,
            name="Radiology",
            category=DiagnosticDepartment.Category.IMAGING,
        )
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/referrals/departments/?category=laboratory")
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["category"] == "laboratory"


@pytest.mark.django_db
class TestDiagnosticMethodsAPI:
    def test_list_returns_methods(self, api_client, doctor, method):
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/referrals/methods/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["code"] == "CBC"

    def test_filter_by_department(self, api_client, doctor, department, method):
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/referrals/methods/?department={department.id}")
        assert response.json()["count"] == 1

    def test_filter_by_other_department_returns_empty(
        self, api_client, doctor, department, method, other_department
    ):
        api_client.force_authenticate(user=doctor)
        # Other department is in another org, doctor shouldn't see it
        response = api_client.get(f"/api/referrals/methods/?department={other_department.id}")
        assert response.json()["count"] == 0


# ---------------------------------------------------------------------------
# Referral with department / method
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestReferralWithDiagnostics:
    def test_create_auto_fills_type_and_title(
        self, api_client, doctor, case, organization, department, method
    ):
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/referrals/",
            {
                "case": case.id,
                "organization": organization.id,
                "department": department.id,
                "method": method.id,
            },
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "lab"  # from department.category
        assert data["title"] == "Complete blood count"  # from method.name
        assert data["department_name"] == "Clinical laboratory"
        assert data["method_name"] == "Complete blood count"

    def test_create_with_mismatched_method_fails(
        self, api_client, doctor, case, organization, department
    ):
        """Method from a different department → 400."""
        other_dept = DiagnosticDepartment.objects.create(
            organization=organization,
            name="Radiology",
            category=DiagnosticDepartment.Category.IMAGING,
        )
        foreign_method = DiagnosticMethod.objects.create(
            department=other_dept,
            code="CT",
            name="Computed tomography",
        )
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/referrals/",
            {
                "case": case.id,
                "organization": organization.id,
                "department": department.id,  # lab
                "method": foreign_method.id,  # CT (radiology)
            },
            format="json",
        )
        assert response.status_code == 400
        assert "method" in response.json()

    def test_create_with_foreign_department_fails(
        self, api_client, doctor, case, organization, other_department
    ):
        """Department from another org → 400."""
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/referrals/",
            {
                "case": case.id,
                "organization": organization.id,
                "department": other_department.id,
            },
            format="json",
        )
        assert response.status_code == 400
        assert "department" in response.json()

    def test_full_fields_round_trip(
        self, api_client, doctor, case, organization, department, method, superuser
    ):
        """Create with all new fields, verify they persist."""
        from django.utils import timezone

        scheduled = timezone.now() + timezone.timedelta(days=3)
        api_client.force_authenticate(user=doctor)
        response = api_client.post(
            "/api/referrals/",
            {
                "case": case.id,
                "organization": organization.id,
                "department": department.id,
                "method": method.id,
                "assigned_to": superuser.id,
                "scheduled_at": scheduled.isoformat(),
                "room": "312",
                "notes": "Fasting required",
            },
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["assigned_to"] == superuser.id
        assert data["room"] == "312"
        assert data["scheduled_at"] is not None


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestReferralFilters:
    def _make_referral(self, case, organization, doctor, department=None, method=None):
        return Referral.objects.create(
            case=case,
            organization=organization,
            type="lab",
            title="X",
            ordered_by=doctor,
            department=department,
            method=method,
        )

    def test_filter_by_department(
        self,
        api_client,
        doctor,
        case,
        organization,
        department,
        method,
        referral,
    ):
        # Create second referral with department
        self._make_referral(case, organization, doctor, department=department, method=method)
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/referrals/?department={department.id}")
        assert response.json()["count"] == 1

    def test_filter_by_method(
        self,
        api_client,
        doctor,
        case,
        organization,
        department,
        method,
    ):
        self._make_referral(case, organization, doctor, department=department, method=method)
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/referrals/?method={method.id}")
        assert response.json()["count"] == 1

    def test_filter_by_assigned_to(
        self,
        api_client,
        doctor,
        case,
        organization,
        department,
        method,
        superuser,
    ):
        r = self._make_referral(case, organization, doctor, department=department, method=method)
        r.assigned_to = superuser
        r.save()
        api_client.force_authenticate(user=doctor)
        response = api_client.get(f"/api/referrals/?assigned_to={superuser.id}")
        assert response.json()["count"] == 1

    def test_filter_by_scheduled_range(
        self,
        api_client,
        doctor,
        case,
        organization,
        department,
        method,
    ):
        from django.utils import timezone

        now = timezone.now()
        r1 = self._make_referral(case, organization, doctor, department, method)
        r1.scheduled_at = now + timezone.timedelta(days=1)
        r1.save()

        r2 = self._make_referral(case, organization, doctor, department, method)
        r2.scheduled_at = now + timezone.timedelta(days=10)
        r2.save()

        api_client.force_authenticate(user=doctor)
        # Use Z suffix instead of +00:00 — the plus sign in URL query
        # strings is interpreted as a space, which Django cannot parse.
        from_iso = (now + timezone.timedelta(hours=1)).isoformat().replace("+00:00", "Z")
        to_iso = (now + timezone.timedelta(days=5)).isoformat().replace("+00:00", "Z")
        response = api_client.get(
            f"/api/referrals/?scheduled_from={from_iso}&scheduled_to={to_iso}"
        )
        assert response.json()["count"] == 1

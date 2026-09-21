import pytest

from apps.referrals.models import Referral


@pytest.mark.django_db
class TestReferralModel:
    def test_default_status_is_ordered(self, referral):
        assert referral.status == "ordered"

    def test_str_with_title(self, referral):
        assert "CT chest with contrast" in str(referral)
        assert "ordered" in str(referral)

    def test_str_without_title_uses_type_display(self, db, case, organization, doctor):
        r = Referral.objects.create(
            case=case,
            organization=organization,
            type=Referral.Type.LAB,
            ordered_by=doctor,
        )
        assert "Laboratory test" in str(r)

    def test_result_fields_default_empty(self, referral):
        assert referral.result_text == ""
        assert referral.result_received_at is None
        assert referral.completed_by is None

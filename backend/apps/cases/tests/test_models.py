import pytest


@pytest.mark.django_db
class TestCancerCaseModel:
    def test_default_status_is_new(self, case):
        assert case.status == "new"

    def test_str_representation(self, case):
        result = str(case)
        assert "Ivan Petrov" in result
        assert "new" in result

    def test_status_cannot_be_assigned_directly(self, case):
        """FSMField(protected=True) must prevent direct assignment."""
        with pytest.raises(AttributeError):
            case.status = "remission"

    def test_stage_stored_as_text(self, case):
        assert case.stage == "IIB"

    def test_tnm_fields(self, case):
        assert case.tnm_t == "T2"
        assert case.tnm_n == "N1"
        assert case.tnm_m == "M0"

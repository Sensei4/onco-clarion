from rest_framework.routers import DefaultRouter

from . import views, views_diagnostics

app_name = "referrals"

router = DefaultRouter()

# Register specific (nested) paths FIRST so they take priority
# over the generic /referrals/{pk}/ pattern from ReferralViewSet.
router.register(
    r"referrals/departments",
    views_diagnostics.DiagnosticDepartmentViewSet,
    basename="diagnostic-department",
)
router.register(
    r"referrals/methods",
    views_diagnostics.DiagnosticMethodViewSet,
    basename="diagnostic-method",
)

# ReferralViewSet LAST — its /referrals/{pk}/ pattern is the
# most generic and would otherwise swallow /referrals/departments/.
router.register(r"referrals", views.ReferralViewSet, basename="referral")

urlpatterns = router.urls

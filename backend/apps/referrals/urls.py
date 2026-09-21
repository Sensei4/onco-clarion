from rest_framework.routers import DefaultRouter

from . import views

app_name = "referrals"

router = DefaultRouter()
router.register(r"referrals", views.ReferralViewSet, basename="referral")

urlpatterns = router.urls

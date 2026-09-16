from rest_framework.routers import DefaultRouter

from . import views

app_name = "cases"

router = DefaultRouter()
router.register(r"cases", views.CancerCaseViewSet, basename="case")

urlpatterns = router.urls

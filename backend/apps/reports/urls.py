from rest_framework.routers import DefaultRouter

from . import views

app_name = "reports"

router = DefaultRouter()
router.register(r"reports", views.ReportViewSet, basename="report")

urlpatterns = router.urls

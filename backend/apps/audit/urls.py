from rest_framework.routers import DefaultRouter

from . import views

app_name = "audit"

router = DefaultRouter()
router.register(r"audit", views.AuditEventViewSet, basename="audit-event")

urlpatterns = router.urls

from rest_framework.routers import DefaultRouter

from . import views

app_name = "documents"

router = DefaultRouter()
router.register(r"documents", views.DocumentViewSet, basename="document")

urlpatterns = router.urls

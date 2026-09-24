from rest_framework.routers import DefaultRouter

from . import views

app_name = "dictionaries"

router = DefaultRouter()
router.register(r"dictionaries/icd11", views.Icd11ViewSet, basename="icd11")

urlpatterns = router.urls

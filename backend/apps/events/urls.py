from rest_framework.routers import DefaultRouter

from . import views

app_name = "events"

router = DefaultRouter()

# Register subtype viewsets FIRST so their specific paths
# (e.g. /events/primary-visits/) are matched before the
# generic /events/{pk}/ pattern from EventViewSet.
router.register(
    r"events/primary-visits",
    views.EventPrimaryVisitViewSet,
    basename="event-primary-visit",
)
router.register(
    r"events/followup-visits",
    views.EventFollowupVisitViewSet,
    basename="event-followup-visit",
)
router.register(
    r"events/observation-visits",
    views.EventObservationVisitViewSet,
    basename="event-observation-visit",
)
router.register(
    r"events/consilia",
    views.EventConsiliumViewSet,
    basename="event-consilium",
)
router.register(
    r"events/hospitalizations",
    views.EventHospitalizationViewSet,
    basename="event-hospitalization",
)
router.register(
    r"events/treatments",
    views.EventTreatmentViewSet,
    basename="event-treatment",
)

# Base event viewset LAST — its /events/{pk}/ pattern
# is the most generic.
router.register(r"events", views.EventViewSet, basename="event")

urlpatterns = router.urls

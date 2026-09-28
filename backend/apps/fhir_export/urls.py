"""URL routing for FHIR export endpoints."""

from django.urls import path

from . import views

app_name = "fhir_export"

urlpatterns = [
    path("Patient/<int:pk>/", views.patient_fhir, name="patient-fhir"),
    path(
        "Patient/<int:pk>/$everything/",
        views.patient_everything,
        name="patient-everything",
    ),
]

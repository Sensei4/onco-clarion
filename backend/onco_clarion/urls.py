from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", include("apps.core.urls")),
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.patients.urls")),
    path("api/", include("apps.cases.urls")),
    path("api/", include("apps.events.urls")),
    path("api/", include("apps.referrals.urls")),
]

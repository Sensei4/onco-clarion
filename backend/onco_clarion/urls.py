from django.conf import settings
from django.conf.urls.static import static
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
    path("api/", include("apps.documents.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

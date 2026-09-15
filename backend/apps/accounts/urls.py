from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "accounts"

# Router for CRUD viewsets
router = DefaultRouter()
router.register(r"organizations", views.OrganizationViewSet, basename="organization")
router.register(r"users", views.UserViewSet, basename="user")

# Auth endpoints (manual views)
auth_patterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.me_view, name="me"),
]

urlpatterns = [
    path("auth/", include(auth_patterns)),
    path("", include(router.urls)),
]

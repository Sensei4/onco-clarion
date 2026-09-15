from django.contrib.auth import authenticate, get_user_model, login, logout
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Organization
from .permissions import IsAdmin
from .serializers import (
    LoginSerializer,
    OrganizationSerializer,
    UserSerializer,
    UserWriteSerializer,
)

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(
        request,
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )
    if user is None:
        return Response(
            {"detail": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    if not user.is_active:
        return Response(
            {"detail": "User account is disabled."},
            status=status.HTTP_403_FORBIDDEN,
        )

    login(request, user)
    return Response(UserSerializer(user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)


class OrganizationViewSet(viewsets.ModelViewSet):
    """CRUD for organizations.

    - Any authenticated user can list/retrieve.
    - Only admins can create/update/delete.
    """

    queryset = Organization.objects.all().order_by("name")
    serializer_class = OrganizationSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsAdmin()]


class UserViewSet(viewsets.ModelViewSet):
    """CRUD for users.

    - Only admins can list/create/update/delete users.
    """

    queryset = User.objects.select_related("organization").order_by("username")
    serializer_class = UserWriteSerializer
    permission_classes = [IsAdmin]

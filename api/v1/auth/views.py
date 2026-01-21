from django.contrib.auth import logout
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from api.v1.auth.serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
)
from app.core.permissions import IsAdminOrSelf


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request: Request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(RegisterSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAdminOrSelf])
def logout_view(request: Request):
    logout(request)

    return Response({"message": "Logged out successfully"})

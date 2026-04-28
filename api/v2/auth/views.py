from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api.v2.auth.serializer import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)
from app.core.permissions import IsAuthenticated
from app.core.security.throttling.auth import LoginThrottle, RegisterThrottle
from django.conf import settings


class CustomTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginThrottle]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        response.set_cookie(
            key="refresh_token",
            value=response.data.get("refresh_token"),
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
        )

        del response.data["refresh_token"]
        return response


class CreateUserAPIView(CreateAPIView):
    throttle_classes = [RegisterThrottle]
    serializer_class = RegisterSerializer


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            raise ValidationError("Refresh token is required")
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as err:
            raise ValidationError("Invalid refresh token") from err

        response = Response(status=status.HTTP_204_NO_CONTENT)

        response.delete_cookie("refresh_token")
        return response


class TokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            raise ValidationError("Refresh token is required")

        try:
            token = RefreshToken(refresh_token)
            response = Response(
                {"access_token": str(token.access_token), "refresh_token": str(token)}
            )
            response.set_cookie(
                key="refresh_token",
                value=str(refresh_token),
                httponly=True,
                secure=not settings.DEBUG,
                max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
                samesite="Lax",
            )

            return response
        except TokenError:
            raise AuthenticationFailed("Invalid or expired token")


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(instance=request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

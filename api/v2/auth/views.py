from api.v2.auth.serializer import CustomTokenObtainPairSerializer, RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from app.core.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CreateUserAPIView(CreateAPIView):
    serializer_class = RegisterSerializer

class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            raise ValidationError("Refresh token is required")
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as err:
            raise ValidationError("Invalid refresh token") from err

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

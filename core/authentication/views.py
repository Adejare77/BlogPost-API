from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from core.authentication.serializers import LoginSerializer, RegisterSerializer
from core.permissions import IsAdminOrSelf

from rest_framework_simplejwt.views import TokenObtainPairView
from core.authentication.serializers import CustomTokenObtainPairSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# # Create your views here.
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def login_view(request: Request):
#     serializer = LoginSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)

#     user = authenticate(
#         email=serializer.validated_data['email'],
#         password=serializer.validated_data['password']
#         )
#     if not user:
#         return Response(
#             {'detail': 'Invalid credentials'},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     # cache user's session into redis
#     login(request, user)
#     return Response({"message": "login Successful"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request: Request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(RegisterSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAdminOrSelf])
def logout_view(request: Request):
    logout(request)

    return Response({'message': 'Logged out successfully'})

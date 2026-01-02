from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from app.core.permissions import IsAuthenticated, IsAdminUser, IsAdminOrSelf
from django.contrib.auth import get_user_model
from api.v2.user.serializer import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound


User = get_user_model()

class UserListAPIView(ListAPIView):
    """
    GET -> user: list all users
    """

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class UserRetrieveAPIView(RetrieveAPIView):
    """
    GET -> user: retrieve a user
    """

    permission_classes = [IsAuthenticated, IsAdminOrSelf]
    serializer_class = UserSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'
    queryset = User.objects.all()


class DisableUserAPIView(APIView):
    """
    POST -> user: disable a user
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            raise NotFound("User not found.")

        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EnableUserAPIView(APIView):
    """
    POST -> user: enable user
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            raise NotFound("User not found.")

        user.is_active = True
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

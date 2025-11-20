from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework import status
from rest_framework.request import Request
from django.contrib.auth import get_user_model
from user.serializer import UserSerializer
from core.permissions import IsAdminOrSelf, IsAdminUser, IsAuthenticated


User = get_user_model()


# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_users(request: Request):
    if not request.user.is_active:
        raise AuthenticationFailed({"detail": "Staff account is disabled."})

    all_users = User.objects.filter(is_staff=False)
    serializer = UserSerializer(all_users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes(([IsAuthenticated, IsAdminOrSelf]))
def get_user_by_id(request: Request, user_id):
    if not request.user.is_active:
        raise AuthenticationFailed({"detail": "User account is disabled."})

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist as e:
        return Response({"error": "Invalid user Id"}, status=status.HTTP_400_BAD_REQUEST)

    # if its a staff or the owner
    IsAdminOrSelf().has_object_permission(request, None, user)

    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def disable_user_account(request: Request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid user ID'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if user.is_staff:
        raise PermissionDenied({'error': "You can't disable a staff account"})

    user.is_active = False
    user.save()

    return Response({'message': f'{user.id} account disabled'})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def enable_user_account(request: Request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist as e:
        return Response({'error': 'Invalid user ID'})

    if user.is_staff:
        raise PermissionDenied({'error': 'You can\'t enable a staff account'})

    user.is_active = True
    user.save()

    return Response({
        'message': f'{user.id} account enabled'
    }, status=status.HTTP_200_OK)

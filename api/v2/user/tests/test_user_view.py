from django.urls import reverse
from rest_framework.test import force_authenticate
from rest_framework import status

from api.v2.user.views import (
    UserListAPIView,
    UserRetrieveAPIView,
    DisableUserAPIView,
    EnableUserAPIView,
)

from api.v2.user.tests.constants import UNAUTHORIZED, FORBIDDEN


# ============================ Test UserListAPIView ==============================
def test_list_users_when_unauthenticated_returns_401(api_rf):
    """GET -> all users by anonymous: returns 401"""
    url = reverse("v2:all-users")
    request = api_rf.get(url)
    view = UserListAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data.get("detail") == UNAUTHORIZED


def test_list_users_by_non_admin_returns_403(api_rf, users):
    """GET -> all users by non admin: returns 403"""
    url = reverse("v2:all-users")
    user_1 = users["user_1"]
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user_1)
    view = UserListAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == FORBIDDEN


def test_list_users_by_admin_returns_200(api_rf, users):
    """GET -> all users by admin: returns 200"""
    url = reverse("v2:all-users")
    request = api_rf.get(url)
    admin = users["admin"]
    force_authenticate(request=request, user=admin)
    view = UserListAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK


# ====================== Test UserRetrieveAPIView ================================
def test_retrieve_user_when_unauthenticated_returns_401(api_rf, users):
    """GET -> retrieve user by anonymous: returns 401"""
    user_1 = users["user_1"]
    url = reverse("v2:user-profile", kwargs={"user_id": user_1.id})
    request = api_rf.get(path=url)
    view = UserRetrieveAPIView.as_view()

    response = view(request, user_id=user_1.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data.get("detail") == UNAUTHORIZED


def test_retrieve_user_as_owner_returns_200(users, api_rf):
    """GET -> retrieve own profile: returns 200"""
    user = users["user_1"]
    url = reverse("v2:user-profile", kwargs={"user_id": user.id})
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = UserRetrieveAPIView.as_view()

    response = view(request, user_id=user.id)

    assert response.status_code == status.HTTP_200_OK


def test_retrieve_user_as_non_owner_returns_403(api_rf, users):
    """GET -> retrieve other's profile: returns 403"""
    user_1 = users["user_1"]
    user_2 = users["user_2"]
    url = reverse("v2:user-profile", kwargs={"user_id": user_1.id})
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user_1)
    view = UserRetrieveAPIView.as_view()

    response = view(request, user_id=user_2.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == FORBIDDEN


def test_retrieve_user_by_admin_returns_200(api_rf, users):
    """GET -> retrieve user's profile by admin: returns 200"""
    user_1 = users["user_1"]
    url = reverse("v2:user-profile", kwargs={"user_id": user_1.id})
    admin = users["admin"]
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=admin)
    view = UserRetrieveAPIView.as_view()

    response = view(request, user_id=user_1.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == str(user_1.id)


# ======================= Test DisableUserAPIView =========================
def test_disable_user_without_authentication_returns_401(api_rf, users):
    """POST -> disable user by anonymous user: returns 401"""
    user_1 = users["user_1"]
    url = reverse("v2:disable-account", args=[user_1.id])
    request = api_rf.post(path=url)
    view = DisableUserAPIView.as_view()

    response = view(request, user_id=user_1.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"] == UNAUTHORIZED


def test_disable_user_as_owner_returns_403(api_rf, users):
    """POST -> disable own account: returns 403"""
    user_1 = users["user_1"]
    url = reverse("v2:disable-account", args=[user_1.id])
    request = api_rf.post(path=url)
    force_authenticate(request=request, user=user_1)
    view = DisableUserAPIView.as_view()

    response = view(request, user_id=user_1.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == FORBIDDEN


def test_disable_user_as_non_owner_returns_403(api_rf, users):
    """POST -> disable other's user account: returns 403"""
    user_1 = users["user_1"]
    user_2 = users["user_2"]
    url = reverse("v2:disable-account", args=[user_1.id])
    request = api_rf.post(path=url)
    force_authenticate(request=request, user=user_2)
    view = DisableUserAPIView.as_view()

    response = view(request, user_id=user_1.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == FORBIDDEN


def test_disable_user_as_admin_returns_204(api_rf, users):
    """POST -> disable user's account as admin: returns 204"""
    user_1 = users["user_1"]
    admin = users["admin"]
    url = reverse("v2:disable-account", args=[user_1.id])
    request = api_rf.post(path=url)
    force_authenticate(request=request, user=admin)
    view = DisableUserAPIView.as_view()

    response = view(request, user_id=user_1.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


# =========================== EnableUserAPIView ====================
def test_enable_user_when_unauthenticated_returns_401(api_rf, users):
    """POST -> enable user as anonymous: returns 401"""
    user_1 = users["user_1"]
    url = reverse("v2:enable-account", args=[user_1.id])
    request = api_rf.post(path=url)
    view = EnableUserAPIView.as_view()

    response = view(request, user_id=user_1.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"] == UNAUTHORIZED


def test_enable_user_as_owner_returns_403(api_rf, users):
    """POST -> enable own account: returns 403"""
    user_1 = users["user_1"]
    url = reverse("v2:enable-account", args=[user_1.id])
    request = api_rf.post(path=url)
    force_authenticate(request=request, user=user_1)
    view = EnableUserAPIView.as_view()

    response = view(request, user_id=user_1.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == FORBIDDEN


def test_enable_user_as_non_owner_returns_403(api_rf, users):
    """POST -> enable other's account: returns 403"""
    user_1 = users["user_1"]
    user_2 = users["user_2"]
    url = reverse("v2:enable-account", args=[user_1.id])
    request = api_rf.post(path=url)
    force_authenticate(request=request, user=user_2)
    view = EnableUserAPIView.as_view()

    response = view(request, user_id=user_1.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == FORBIDDEN


def test_enable_user_as_admin_returns_204(api_rf, users):
    user_2 = users["user_2"]
    admin = users["admin"]
    url = reverse("v2:enable-account", args=[user_2.id])
    request = api_rf.post(path=url)
    force_authenticate(request=request, user=admin)
    view = EnableUserAPIView.as_view()

    response = view(request, user_id=user_2.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT

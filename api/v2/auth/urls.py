from django.urls import path

from api.v2.auth.views import (
    CreateUserAPIView,
    CustomTokenObtainPairView,
    LogoutAPIView,
    MeView,
    TokenRefreshView,
)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("register/", CreateUserAPIView.as_view(), name="sign-up"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
]

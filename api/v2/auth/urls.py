from django.urls import path

from api.v2.auth.views import (
    CreateUserAPIView,
    CustomTokenObtainPairView,
    LogoutAPIView,
)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("register/", CreateUserAPIView.as_view(), name="sign-up"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]

from django.urls import path

from api.v2.user.views import (
    DisableUserAPIView,
    EnableUserAPIView,
    UserListAPIView,
    UserRetrieveAPIView,
)

urlpatterns = [
    path("", UserListAPIView.as_view(), name="all-users"),
    path("<uuid:user_id>/", UserRetrieveAPIView.as_view(), name="user-profile"),
    path(
        "<uuid:user_id>/disable/", DisableUserAPIView.as_view(), name="disable-account"
    ),
    path("<uuid:user_id>/enable/", EnableUserAPIView.as_view(), name="enable-account"),
]

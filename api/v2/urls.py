from django.urls import path, include
from drf_spectacular.views import (
    SpectacularSwaggerView,
    SpectacularRedocView,
    SpectacularAPIView,
)

app_name = "v2"

urlpatterns = [
    path("", include("api.v2.comment.urls")),
    path("", include("app.core.authentication.urls")),
    path("", include("api.v2.like.urls")),
    path("posts/", include("api.v2.post.urls")),
    path("users/", include("api.v2.user.urls")),
    path("schema/swagger/", SpectacularSwaggerView.as_view(), name="swagger"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

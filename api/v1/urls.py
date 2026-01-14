from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

app_name = "v1"

urlpatterns = [
    path("", include("api.v1.comment.urls")),
    path("", include("app.core.authentication.urls")),
    path("", include("api.v1.like.urls")),
    path("posts/", include("api.v1.post.urls")),
    path("users/", include("api.v1.user.urls")),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger/", SpectacularSwaggerView.as_view(), name="swagger"),
]

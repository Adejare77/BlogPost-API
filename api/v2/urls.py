from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

app_name = "v2"

urlpatterns = [
    path("", include("api.v2.comment.urls")),
    path("", include("app.core.authentication.urls")),
    path("", include("api.v2.like.urls")),
    path("posts/", include("api.v2.post.urls")),
    path("users/", include("api.v2.user.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="v2:schema"),
        name="swagger",
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="v2:schema"), name="redoc"),
]

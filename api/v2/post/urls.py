from django.urls import path

from api.v2.post.views import (
    PopularPostListAPIView,
    PostListCreateAPIView,
    PostRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path("", PostListCreateAPIView.as_view(), name="posts"),
    path(
        "<uuid:post_id>/",
        PostRetrieveUpdateDestroyAPIView.as_view(),
        name="post-detail",
    ),
    path("popular/", PopularPostListAPIView.as_view(), name="popular"),
]

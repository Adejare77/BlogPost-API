from django.urls import path

from api.v2.like.views import LikePostAPIView, LikeCommentAPIView

urlpatterns = [
    path("posts/<uuid:post_id>/likes/", LikePostAPIView.as_view(), name="like-post"),
    path(
        "comments/<uuid:comment_id>/likes/",
        LikeCommentAPIView.as_view(),
        name="like-comment",
    ),
]

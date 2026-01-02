from django.urls import path

from api.v2.like.views import (
    LikePostAPIView,
    LikeCommentAPIView
)

urlpatterns = [
    path("posts/<uuid:post_id>/like/", LikePostAPIView.as_view(), name="like-post"),
    path("comments/<uuid:comment_id>/like/", LikeCommentAPIView.as_view(), name="like-comment"),
]

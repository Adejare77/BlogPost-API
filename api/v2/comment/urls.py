from django.urls import path

from api.v2.comment.views import (
    CommentListCreateAPIView,
    CommentRetrieveUpdateDestroyAPIView,
    ReplyListCreateAPIView,
    ReplyRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path(
        "posts/<uuid:post_id>/comments/",
        CommentListCreateAPIView.as_view(),
        name="comments",
    ),
    path(
        "comments/<uuid:comment_id>/",
        CommentRetrieveUpdateDestroyAPIView.as_view(),
        name="comment-detail",
    ),
    path(
        "comments/<uuid:comment_id>/replies/",
        ReplyListCreateAPIView.as_view(),
        name="replies",
    ),
    path(
        "replies/<uuid:reply_id>/",
        ReplyRetrieveUpdateDestroyAPIView.as_view(),
        name="reply-detail",
    ),
]

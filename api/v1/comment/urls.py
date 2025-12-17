from django.urls import path

from api.v1.comment import views

urlpatterns = [
    path("posts/<uuid:post_id>/comments/", views.post_comments, name="comments"),
    path(
        "comments/<uuid:comment_id>/", views.post_comment_detail, name="comment-detail"
    ),
    path("comments/<uuid:comment_id>/replies/", views.comment_replies, name="replies"),
    path("replies/<uuid:reply_id>/", views.comment_reply_details, name="reply-detail"),
]

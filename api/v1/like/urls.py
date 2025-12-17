from django.urls import path

from api.v1.like import views

urlpatterns = [
    path("posts/<uuid:post_id>/like/", views.like_post, name="like-post"),
    path("comments/<uuid:comment_id>/like/", views.like_comment, name="like-comment"),
]

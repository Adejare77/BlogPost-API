from django.urls import path

from api.v1.post import views

urlpatterns = [
    path("", views.post_list, name="posts"),
    path("<uuid:post_id>/", views.post_detail, name="post-detail"),
    path("popular/", views.get_popular_posts, name="popular"),
]

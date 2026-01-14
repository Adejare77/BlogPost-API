from django.urls import reverse
from rest_framework import status
from rest_framework.test import force_authenticate

from api.v2.like.tests.constants import UNAUTHORIZED
from api.v2.like.views import LikeCommentAPIView, LikePostAPIView
from app.like.models import Like


def test_like_post_when_unauthenticated_returns_401(posts, api_rf):
    post = posts["post_1"]

    url = reverse("v2:like-post", args=[post.id])
    request = api_rf.post(path=url)
    view = LikePostAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"] == UNAUTHORIZED


def test_like_post_as_user_returns_200(users, posts, api_rf):
    user = users["user_3"]
    post = posts["post_2"]

    url = reverse("v2:like-post", args=[post.id])
    request = api_rf.post(path=url)
    force_authenticate(request=request, user=user)
    view = LikePostAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_200_OK
    assert post.likes.filter(user_id=user.id, object_id=post.id).exists()


def test_like_post_more_than_once_returns_200(likes, api_rf):
    liked = likes["post_like"]
    user = liked.user
    post_id = liked.object_id
    old_like_count = Like.objects.filter(object_id=post_id).count()

    url = reverse("v2:like-post", args=[post_id])
    request = api_rf.post(path=url)
    force_authenticate(request=request, user=user)
    view = LikePostAPIView.as_view()

    response = view(request, post_id=post_id)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["like_count"] == old_like_count


def test_delete_liked_post_when_unauthenticated_returns_401(likes, api_rf):
    liked = likes["post_like"]
    post_id = liked.object_id

    url = reverse("v2:like-post", args=[post_id])
    request = api_rf.delete(path=url)
    view = LikePostAPIView.as_view()

    response = view(request, post_id=post_id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"] == UNAUTHORIZED


def test_delete_liked_post_as_user_returns_200(db, likes, api_rf):
    liked = likes["post_like"]
    user = liked.user
    post_id = liked.object_id
    old_like_count = Like.objects.filter(object_id=post_id).count()

    url = reverse("v2:like-post", args=[post_id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = LikePostAPIView.as_view()

    response = view(request, post_id=post_id)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["like_count"] == old_like_count - 1


def test_delete_liked_post_for_non_owner_returns_403(users, likes, api_rf):
    liked = likes["post_like"]
    user = users["user_1"]
    post_id = liked.object_id
    old_like_count = Like.objects.filter(object_id=post_id).count()

    url = reverse("v2:like-post", args=[post_id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = LikePostAPIView.as_view()

    response = view(request, post_id=post_id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["like_count"] == old_like_count


def test_delete_unliked_post_returns_404(users, posts, api_rf):
    user = users["user_2"]
    post = posts["post_1"]
    old_like_count = Like.objects.filter(object_id=post.id).count()

    url = reverse("v2:like-post", args=[post.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = LikePostAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["like_count"] == old_like_count


# ================= LikeCommentAPIView ==================


def test_like_comment_when_unauthenticated_returns_401(likes, api_rf):
    comment = likes["comment_like"]

    url = reverse("v2:like-comment", args=[comment.id])
    request = api_rf.post(path=url)
    view = LikeCommentAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"] == UNAUTHORIZED


def test_like_comment_as_user_returns_200(users, comments, api_rf):
    user = users["user_3"]
    comment = comments["comment_2"]

    url = reverse("v2:like-post", args=[comment.id])
    request = api_rf.post(path=url)
    force_authenticate(request=request, user=user)
    view = LikeCommentAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_200_OK
    assert comment.likes.filter(user_id=user.id, object_id=comment.id).exists()


def test_like_comment_more_than_once_returns_200(likes, api_rf):
    liked = likes["comment_like"]
    user = liked.user
    comment_id = liked.object_id
    old_like_count = Like.objects.filter(object_id=comment_id).count()

    url = reverse("v2:like-comment", args=[comment_id])
    request = api_rf.post(path=url)
    force_authenticate(request=request, user=user)
    view = LikeCommentAPIView.as_view()

    response = view(request, comment_id=comment_id)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["like_count"] == old_like_count


def test_delete_liked_comment_when_unauthenticated_returns_401(likes, api_rf):
    liked = likes["comment_like"]
    comment_id = liked.object_id

    url = reverse("v2:like-comment", args=[comment_id])
    request = api_rf.delete(path=url)
    view = LikeCommentAPIView.as_view()

    response = view(request, comment_id=comment_id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"] == UNAUTHORIZED


def test_delete_liked_comment_as_user_returns_200(likes, api_rf):
    liked = likes["comment_like"]
    user = liked.user
    comment_id = liked.object_id
    old_like_count = Like.objects.filter(object_id=comment_id).count()

    url = reverse("v2:like-post", args=[comment_id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = LikeCommentAPIView.as_view()

    response = view(request, comment_id=comment_id)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["like_count"] == old_like_count - 1


def test_delete_liked_comment_for_non_owner_returns_403(users, likes, api_rf):
    liked = likes["comment_like"]
    user = users["user_1"]
    comment_id = liked.object_id
    old_like_count = Like.objects.filter(object_id=comment_id).count()

    url = reverse("v2:like-comment", args=[comment_id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = LikeCommentAPIView.as_view()

    response = view(request, comment_id=comment_id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["like_count"] == old_like_count


def test_delete_unliked_comment_returns_404(users, comments, api_rf):
    user = users["user_2"]
    comment = comments["comment_1"]
    old_like_count = Like.objects.filter(object_id=comment.id).count()

    url = reverse("v2:like-post", args=[comment.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = LikeCommentAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["like_count"] == old_like_count

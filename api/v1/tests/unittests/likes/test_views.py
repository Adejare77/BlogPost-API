from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from api.v1.like import views
from app.comment.models import Comment
from app.post.models import Post


class TestLikePostView(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            full_name="ABC", email="testing@gmail.com", password="testing"
        )
        self.post = Post.objects.create(
            author=self.user,
            content="This is a sample content",
            title="Introduction to Mathematics",
        )

        self.factory = APIRequestFactory()

    def test_like_post_without_auth(self):
        """Test liking a post without authentication"""
        url = reverse("v1:like-post", args=[self.post.id])
        request = self.factory.post(path=url)

        response = views.like_post(request, self.post.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided"
        )

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes.count(), 0)

    def test_like_post_with_auth(self):
        """Test liking a post with authentication"""
        url = reverse("v1:like-post", args=[self.post.id])
        request = self.factory.post(path=url)
        force_authenticate(request=request, user=self.user)

        response = views.like_post(request, self.post.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.post.refresh_from_db()
        like_count = self.post.likes.count()
        self.assertEqual(like_count, 1)

    def test_user_cannot_like_more_than_once(self):
        """Test liking more than once"""
        url = reverse("v1:like-post", args=[self.post.id])
        request = self.factory.post(path=url)
        force_authenticate(request=request, user=self.user)

        # first like
        views.like_post(request, self.post.id)
        # second like
        response = views.like_post(request, self.post.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Post already liked")

        self.post.refresh_from_db()
        like_count = self.post.likes.count()
        self.assertEqual(like_count, 1)

    def test_delete_liked_post_without_auth(self):
        """Test deleting like without auth"""
        url = reverse("v1:like-post", args=[self.post.id])
        request = self.factory.delete(path=url)

        response = views.like_post(request, self.post.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided"
        )

    def test_delete_liked_post_with_auth(self):
        """Test deleting post with authentication"""
        # first like the post
        url = reverse("v1:like-post", args=[self.post.id])
        request = self.factory.post(path=url)
        force_authenticate(request=request, user=self.user)

        response = views.like_post(request, self.post.id)
        self.post.refresh_from_db()

        like_count = self.post.likes.count()

        # delete liked post

        request = self.factory.delete(path=url)
        force_authenticate(request=request, user=self.user)

        response = views.like_post(request, self.post.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes.count(), like_count - 1)


class TestLikeCommentView(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            full_name="ABC", email="testing@gmail.com", password="testing"
        )
        self.post = Post.objects.create(
            author=self.user,
            content="This is a sample content",
            title="Introduction to Mathematics",
        )
        self.comment = Comment.objects.create(
            author=self.user, content="This is a nice write up", post=self.post
        )
        self.factory = APIRequestFactory()

    def test_like_comment_without_auth(self):
        """Test liking a comment without authentication"""
        url = reverse("v1:like-comment", args=[self.comment.id])
        request = self.factory.post(url)

        response = views.like_comment(request, self.comment.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided"
        )

    def test_like_comment_with_auth(self):
        """Test liking a comment with authentication"""
        url = reverse("v1:like-comment", args=[self.comment.id])
        request = self.factory.post(url)
        force_authenticate(request=request, user=self.user)

        response = views.like_comment(request, self.comment.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.comment.refresh_from_db()

        self.assertEqual(self.comment.likes.count(), 1)

    def test_user_cannot_like_comment_more_than_once(self):
        """Test liking comment more than once"""
        url = reverse("v1:like-comment", args=[self.comment.id])
        request = self.factory.post(path=url)
        force_authenticate(request=request, user=self.user)

        # first like
        views.like_comment(request, self.comment.id)
        # second like
        response = views.like_comment(request, self.comment.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Comment already liked")

        self.post.refresh_from_db()
        self.assertEqual(self.comment.likes.count(), 1)

    def test_delete_comment_without_auth(self):
        """Test deleting like without auth"""
        pass

    def test_delete_comment_with_auth(self):
        """Test deleting comment with authentication"""
        # first like the comment
        url = reverse("v1:like-comment", args=[self.comment.id])
        request = self.factory.post(path=url)
        force_authenticate(request=request, user=self.user)

        response = views.like_comment(request, self.comment.id)
        self.comment.refresh_from_db()

        like_count = self.comment.likes.count()

        # delete liked comment

        request = self.factory.delete(path=url)
        force_authenticate(request=request, user=self.user)

        response = views.like_comment(request, self.comment.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.likes.count(), like_count - 1)

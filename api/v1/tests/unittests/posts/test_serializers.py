from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from app.post.models import Post
from api.v1.post.serializer import PostDetailSerializer, PostListSerializer


class TestPostListSerializer(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            full_name="ABCD", email="testing@gmail.com", password="testing"
        )
        self.post = Post.objects.create(
            author=self.user,
            content="This is my post on my Country",
            title="The Politics",
            is_published=True,
        )

    def test_serializer_uses_attached_attributes(self):
        self.post.excerpt = self.post.content[:5]
        self.post.like_count = 33
        self.post.comment_count = 13

        ser = PostListSerializer(instance=self.post)

        self.assertSetEqual(
            set(ser.data.keys()),
            {
                "id",
                "title",
                "excerpt",
                "author",
                "likes",
                "comment_count",
                "is_published",
                "created_at",
            },
        )
        self.assertEqual(ser.data["likes"], 33)


class TestPostDetailSerializer(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            full_name="ABCD", email="testing@gmail.com", password="testing"
        )
        self.post = Post.objects.create(
            author=self.user,
            content="This is my post on my Country",
            title="The Politics",
            is_published=True,
        )

    def test_serializer_uses_attached_attributes(self):
        self.post.like_count = 100
        self.post.top_comments = []
        self.post.comment_count = 0

        ser = PostDetailSerializer(instance=self.post)

        self.assertSetEqual(
            set(ser.data.keys()),
            {
                "id",
                "author",
                "title",
                "content",
                "is_published",
                "likes",
                "comment_count",
                "top_comments",
                "created_at",
            },
        )
        self.assertEqual(ser.data["likes"], 100)
        self.assertEqual(ser.data["comment_count"], 0)

    def test_partial_update_with_empty_content_rejected(self):
        data = {"contet": ""}
        ser = PostDetailSerializer(instance=self.post, data=data)

        self.assertFalse(ser.is_valid())
        self.assertEqual(ser.instance.content, self.post.content)

    def test_partial_update_missing_content_allowed(self):
        data = {}
        ser = PostDetailSerializer(instance=self.post, data=data, partial=True)

        self.assertTrue(ser.is_valid())
        self.assertEqual(ser.data["content"], self.post.content)

    def test_serializer_skips_read_attributes(self):
        ser = PostDetailSerializer(instance=self.post)

        self.assertSetEqual(
            set(ser.data.keys()),
            {"id", "author", "title", "content", "is_published", "created_at"},
        )

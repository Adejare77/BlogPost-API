from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from app.comment.models import Comment
from app.comment.serializer import (
    CommentDetailSerializer,
    CommentListSerializer,
    ReplyDetailSerializer,
    ReplyListSerializer,
)
from app.post.models import Post


class TestCommentListSerializer(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            full_name="ABC", email="testing@gmail.com", password="testing"
        )
        self.post = Post.objects.create(
            title="This is a Post",
            content="This is a content to the given title",
            author=self.user,
        )
        self.comment = Comment.objects.create(
            post=self.post, content="This is a Paragraph page", author=self.user
        )

    def test_serializer_uses_attached_attributes(self):
        self.comment.excerpt = self.comment.content[:10]
        self.comment.reply_count = 2
        self.comment.like_count = 6

        ser = CommentListSerializer(instance=self.comment)

        self.assertSetEqual(
            set(ser.data.keys()),
            {"id", "author", "post", "excerpt", "reply_count", "likes", "created_at"},
        )

        self.assertIsNone(ser.instance.parent)


class TestCommentDetailSerializer(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            full_name="ABC", email="testing@gmail.com", password="testing"
        )
        self.post = Post.objects.create(
            title="This is a Post",
            content="This is a content to the given title",
            author=self.user,
        )
        self.comment = Comment.objects.create(
            post=self.post, content="This is a Paragraph page", author=self.user
        )

    def test_partial_update_with_empty_content_rejected(self):
        data = {"content": ""}

        ser = CommentDetailSerializer(data=data)

        self.assertFalse(ser.is_valid())
        self.assertIn("content field cannot be empty", ser.errors["content"][0])

    def test_partial_update_missing_content_allowed(self):
        data = {}

        ser = CommentDetailSerializer(data=data, instance=self.comment, partial=True)

        self.assertTrue(ser.is_valid())
        self.assertEqual(ser.data["content"], self.comment.content)

    def test_serializer_uses_attached_attributes(self):
        self.comment.top_replies = []
        self.comment.reply_count = 0
        self.comment.like_count = 15

        ser = CommentDetailSerializer(instance=self.comment)

        self.assertSetEqual(
            set(ser.data.keys()),
            {
                "id",
                "author",
                "post",
                "content",
                "top_replies",
                "reply_count",
                "likes",
                "created_at",
            },
        )

    def test_serializer_skips_read_attributes(self):
        self.comment.like_count = 0
        ser = CommentDetailSerializer(instance=self.comment)

        self.assertSetEqual(
            set(ser.data.keys()),
            {"id", "author", "post", "likes", "content", "created_at"},
        )

    def test_serializer_creates_comment(self):
        data = {"content": "This is the Second Comment"}
        ser = CommentDetailSerializer(data=data)

        self.assertTrue(ser.is_valid())
        ser.save(post=self.post, author=self.user)

        self.assertEqual(ser.data["content"], data["content"])
        self.assertEqual(ser.data["author"], self.user.id)
        self.assertEqual(ser.data["post"], self.post.isbn)


class TestReplyListSerializer(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            full_name="ABC", email="testing@gmail.com", password="testing"
        )
        self.post = Post.objects.create(
            title="This is a Post",
            content="This is a content to the given title",
            author=self.user,
        )
        self.comment = Comment.objects.create(
            post=self.post, content="This is a Paragraph page", author=self.user
        )
        self.reply = Comment.objects.create(
            post=self.post,
            content="I couldn't agree more with this comment",
            author=self.user,
            parent=self.comment,
        )

    def test_serializer_uses_attached_attributes(self):
        self.reply.excerpt = self.reply.content[:10]
        self.reply.like_count = 0

        ser = ReplyListSerializer(instance=self.reply)

        self.assertSetEqual(
            set(ser.data.keys()), {"id", "author", "excerpt", "likes", "created_at"}
        )

        self.assertIsNotNone(ser.instance.parent)


class TestReplyDetailSerializer(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            full_name="ABC", email="testing@gmail.com", password="testing"
        )
        self.post = Post.objects.create(
            title="This is a Post",
            content="This is a content to the given title",
            author=self.user,
        )
        self.comment = Comment.objects.create(
            post=self.post, content="This is a Paragraph page", author=self.user
        )
        self.reply = Comment.objects.create(
            post=self.post,
            content="This is a reply to a comment",
            author=self.user,
            parent=self.comment,
        )

    def test_serializer_uses_all_attributes(self):
        self.reply.like_count = 1
        ser = ReplyDetailSerializer(instance=self.reply)

        self.assertSetEqual(
            set(ser.data.keys()),
            {"id", "author", "content", "parent", "likes", "created_at"},
        )

    def test_partial_update_with_empty_content_rejected(self):
        data = {"content": ""}

        ser = ReplyDetailSerializer(data=data)
        ser = ReplyDetailSerializer(instance=self.reply, data=data)

        self.assertFalse(ser.is_valid())
        self.assertIn("content field cannot be empty", ser.errors["content"][0])

    def test_partial_update_missing_content_allowed(self):
        data = {}

        ser = ReplyDetailSerializer(data=data, instance=self.reply, partial=True)

        self.assertTrue(ser.is_valid())
        self.assertEqual(ser.data["content"], self.reply.content)

    def test_serializer_skips_read_attributes(self):
        self.comment.like_count = 3
        ser = ReplyDetailSerializer(instance=self.comment)

        self.assertSetEqual(
            set(ser.data.keys()),
            {"id", "author", "content", "parent", "likes", "created_at"},
        )

    def test_serializer_creates_reply_to_comment(self):
        data = {"content": "This is another reply"}
        ser = ReplyDetailSerializer(data=data)

        self.assertTrue(ser.is_valid())
        ser.save(post=self.post, author=self.user, parent=self.comment)

        self.assertEqual(ser.data["content"], data["content"])
        self.assertEqual(ser.data["author"], self.user.id)
        self.assertEqual(ser.instance.post, self.post)
        self.assertIsNotNone(ser.data["parent"])

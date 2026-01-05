from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from app.comment.models import Comment
from app.like.models import Like
from app.post.models import Post


class TestLikeModel(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            full_name="ABCD", email="testing@gmail.com", password="testing"
        )
        self.post = Post.objects.create(
            author=self.user,
            content="This is an introduction to the first part of our lesson",
            title="Introduction",
        )
        self.comment = Comment.objects.create(
            author=self.user, content="Nice exactly a nice write-up", post=self.post
        )

    def test_create_a_post_like(self):
        """Test liking a post"""
        Like.objects.create(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Post),
            object_id=self.post.id,
        )

        self.post.refresh_from_db()

        self.assertEqual(self.post.likes.count(), 1)

    def test_create_a_comment_like(self):
        """Test liking a comment"""
        Like.objects.create(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.comment.id,
        )

        self.comment.refresh_from_db()

        self.assertEqual(self.comment.likes.count(), 1)

    # def test_delete_a_liked_post(self):
    #     """ test deleting a liked post """
    #     like = Like.objects.create(
    #         user=self.user,
    #         content_type=ContentType.objects.get_for_model(Post),
    #         object_id=self.post.id
    #     )
    #     like.delete()

    #     # self.assertEqual(like.count())

    # def test_delete_a_liked_comment(self):
    #     """ test deleting a liked comment """
    #     pass

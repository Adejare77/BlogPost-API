from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from comment.models import Comment
from post.models import Post


class CommentModelTests(TestCase):
    def setUp(self):
        """Set up user, post, and comments"""
        self.user1 = get_user_model().objects.create_user(
            full_name="ABCD", email="testing1@gmail.com", password="testing123"
        )

        self.post1 = Post.objects.create(
            title="Immigration in Nigeria",
            content="""
            The issue concerning immigration in Nigeria is about high time
            this is taken seriously. As a third country still developing, the
            Nigerian Government should invest heavily in its local products.
            """,
            is_published=True,
            author=self.user1,
        )
        self.user2 = get_user_model().objects.create_user(
            full_name="CDE", email="testing2@gmail.com", password="testing123"
        )

    def test_create_a_comment(self):
        """Create a comment to a post"""
        data = {
            "content": "This is a very interesting blog. Love it!!",
            "author": self.user2,
            "post": self.post1,
        }
        comment = Comment.objects.create(**data)

        self.assertEqual(comment.author, data["author"])
        self.assertEqual(comment.content, data["content"])
        self.assertEqual(comment.post, data["post"])
        self.assertEqual(comment.parent, None)

    def test_delete_a_comment(self):
        """Delete a comment from a post"""
        data = {
            "content": "This is a very interesting blog. Love it!!",
            "author": self.user2,
            "post": self.post1,
        }
        comment = Comment.objects.create(**data)

        self.assertEqual(comment.author, data["author"])
        comment.delete()
        self.assertTrue(comment.DoesNotExist)


class CommentModelValidationTests(TestCase):
    def setUp(self):
        """Set up user, post, and comments"""
        self.user1 = get_user_model().objects.create_user(
            full_name="ABCD", email="testing1@gmail.com", password="testing123"
        )

        self.post1 = Post.objects.create(
            title="Immigration in Nigeria",
            content="""
            The issue concerning immigration in Nigeria is about high time
            this is taken seriously. As a third country still developing, the
            Nigerian Government should invest heavily in its local products.
            """,
            is_published=True,
            author=self.user1,
        )

    def test_missing_content_raises_error(self):
        """Test missing content"""
        data = {
            "author": self.user1,
            "post": self.post1,
        }

        with self.assertRaisesMessage(ValidationError, "content field cannot be empty"):
            Comment.objects.create(**data)

    def test_missing_post_raises_error(self):
        """Test missing post"""
        data = {
            "content": "This is a very interesting blog. Love it!!",
            "author": self.user1,
        }
        with self.assertRaises(ValidationError):
            Comment.objects.create(**data)

    def test_missing_author_raises_error(self):
        """Test missing author"""
        data = {
            "content": "This is a very interesting blog. Love it!!",
            "post": self.post1,
        }
        with self.assertRaises(ValidationError):
            Comment.objects.create(**data)

    def test_missing_parent(self):
        """Test missing parent"""
        data = {
            "content": "This is a very interesting blog. Love it!!",
            "author": self.user1,
            "post": self.post1,
        }
        comment = Comment.objects.create(**data)
        self.assertEqual(comment.parent, None)

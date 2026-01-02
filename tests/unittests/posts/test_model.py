from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from app.post.models import Post


class PostModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            **{"full_name": "ABC", "email": "testing@gmail.com", "password": "1234"}
        )

    def test_create_post(self):
        """Test create a post"""
        data = {
            "title": "Learning Curve",
            "content": "A mathematical Concept",
            "author": self.user,
        }
        post = Post.objects.create(**data)

        self.assertEqual(post.title, data["title"])
        self.assertEqual(post.content, data["content"])
        self.assertEqual(post.author, data["author"])
        self.assertFalse(post.is_published)
        self.assertIsNotNone(post.id)


class PostModelValidationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            **{"full_name": "ABC", "email": "testing@gmail.com", "password": "1234"}
        )

    def test_missing_title_raises_error(self):
        """Test missing title validation"""
        data = {"content": "A mathematical Concept", "author": self.user}

        with self.assertRaises(ValidationError) as cm:
            Post.objects.create(**data)

        self.assertIn("title field cannot be empty", cm.exception.messages[0])

    def test_blank_title_raises_error(self):
        """Test blank title validation"""
        data = {"title": "", "content": "A mathematical Concpet", "author": self.user}

        with self.assertRaises(ValidationError) as cm:
            Post.objects.create(**data)

        self.assertIn("title field cannot be empty", cm.exception.messages[0])

    def test_more_than_100_title_characters_raises_error(self):
        """Test blank title validation"""
        data = {
            "title": """
            the title is not meant to accept more than 100 characters in length. For
            example this given title character is definitely more than 100 characters
            """,
            "content": "A mathematical concept",
            "author": self.user,
        }

        with self.assertRaisesMessage(
            ValidationError, "cannot accept more than 50 characters"
        ):
            Post(**data).save()

    def test_missing_content_raises_error(self):
        """Test missing content validation"""
        data = {"title": "Linear Curve", "author": self.user}

        with self.assertRaisesMessage(ValidationError, "content field cannot be empty"):
            Post.objects.create(**data)

    def test_blank_content_raises_error(self):
        """Test blank content validation"""
        data = {"title": "Linear Curve", "author": self.user}

        with self.assertRaisesMessage(ValidationError, "content field cannot be empty"):
            Post(**data).save()  # Post.objects.create(**data)

    def test_missing_is_published_defaults_to_false(self):
        """Test missing is_published validation"""
        data = {
            "title": "Linear Curve",
            "author": self.user,
            "content": "A mathematical concept",
        }

        post = Post.objects.create(**data)
        self.assertFalse(post.is_published)

    def test_true_in_is_published(self):
        """Test missing is_published validation"""
        data = {
            "title": "Linear Curve",
            "author": self.user,
            "content": "A mathematical concept",
            "is_published": True,
        }

        post = Post.objects.create(**data)
        self.assertTrue(post.is_published)

    def test_empty_string_val_for_is_published(self):
        """Test giving string value to is_published"""
        data = {
            "title": "Linear Curve",
            "author": self.user,
            "content": "A mathematical concept",
            "is_published": "",
        }

        with self.assertRaises(ValidationError):
            Post.objects.create(**data)

    def test_string_val_for_is_published(self):
        """Test giving string value to is_published"""
        data = {
            "title": "Linear Curve",
            "author": self.user,
            "content": "A mathematical concept",
            "is_published": "some_value",
        }

        with self.assertRaises(ValidationError):
            Post.objects.create(**data)

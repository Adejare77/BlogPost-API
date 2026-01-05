from api.v2.post.serializer import (
    PostListSerializer,
    PostCreateSerializer,
    PostDetailSerializer,
)

from app.post.models import Post
from django.contrib.auth import get_user_model
import pytest
from rest_framework import serializers


class TestPostCreateSerializer:
    def test_valid_data_validates_successfully(self):
        data = {"content": "Valid Content", "title": "Valid Title"}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid() is True

    def test_missing_title_fails_validation(self):
        data = {
            "content": "Valid Content",
        }

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_empty_title_fails_validation(self):
        data = {"content": "Valid Content", "title": ""}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_missing_content_fails_validation(self):
        data = {"title": "Valid title", "is_published": False}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_empty_content_fails_validation(self):
        data = {"title": "Valid title", "content": "", "is_published": True}

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_missing_is_published_defaults_to_false(self, users, posts):
        data = {
            "title": "Valid title",
            "content": "Valid Content",
        }

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid() is True

        post = serializer.save(author=users["user_1"])

        assert post.is_published == False

    def test_is_published_only_accepts_bool(self):
        data = {
            "title": "Valid title",
            "content": "valid content",
            "is_published": "invalid_status",
        }

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_serialization_includes_expected_fields(self, users):
        data = {
            "title": "Valid title",
            "content": "Valid Content",
            "is_published": True,
        }

        serializer = PostCreateSerializer(data=data)
        assert serializer.is_valid() is True

        post = serializer.save(author=users["user_2"])

        model_fields = {f.name for f in post._meta.get_fields()}
        expected_field = {
            "id",
            "author",
            "content",
            "title",
            "is_published",
            "created_at",
        }

        assert expected_field.issubset(model_fields)

    # def test_sensitive_fields_excluded(self):
    #     pass


class TestPostListSerializer:
    def test_serialization_includes_expected_fields(self, db):
        expected_fields = {
            "id",
            "author",
            "title",
            "excerpt",
            "likes",
            "comment_count",
            "is_published",
            "created_at",
        }

        posts = Post.objects.all()

        ser = PostListSerializer(instance=posts, many=True)
        for result in ser.data:
            assert expected_fields == set(result.keys())

    def test_serialization_fields_are_read_only(self):
        ser = PostListSerializer()

        writable_fields = {
            name for name, field in ser.fields.items() if not field.read_only
        }

        assert writable_fields == set()


class TestPostDetailSerializer:
    def test_content_field_can_be_updated(self, posts):
        post = posts["post_1"]
        data = {"content": "This is the latest content update"}

        ser = PostDetailSerializer(instance=post, data=data, partial=True)
        ser.is_valid()
        ser.save()

        post.refresh_from_db()
        assert post.content == data["content"]

    def test_blank_content_cannot_be_updated(self, posts):
        post = posts["post_1"]
        data = {"content": ""}

        ser = PostDetailSerializer(instance=post, data=data, partial=True)

        with pytest.raises(serializers.ValidationError) as exc_info:
            ser.is_valid(raise_exception=True)

        assert "content" in exc_info.value.detail
        assert exc_info.value.detail["content"][0] == "content field cannot be empty"

    def test_title_field_can_be_updated(self, posts):
        post = posts["post_1"]

        data = {"title": "This is the latest title update"}

        ser = PostDetailSerializer(instance=post, data=data, partial=True)
        ser.is_valid()
        ser.save()

        post.refresh_from_db()

        assert post.title == data["title"]

    def test_blank_title_cannot_be_updated(self, posts):
        post = posts["post_1"]
        data = {"title": ""}

        ser = PostDetailSerializer(instance=post, data=data, partial=True)

        with pytest.raises(serializers.ValidationError) as exc_info:
            ser.is_valid(raise_exception=True)

        assert "title" in exc_info.value.detail
        assert exc_info.value.detail["title"][0] == "title field cannot be empty"

    def test_is_published_field_can_be_updated(self, posts):
        post = posts["post_1"]
        data = {"is_published": False}
        ser = PostDetailSerializer(instance=post, data=data, partial=True)

        assert ser.is_valid(), ser.errors
        ser.save()

        post.refresh_from_db()
        assert post.is_published == data["is_published"]

    def test_blank_is_published_cannot_be_updated(self, posts):
        post = posts["post_1"]
        data = {"is_published": ""}
        ser = PostDetailSerializer(instance=post, data=data, partial=True)

        with pytest.raises(serializers.ValidationError) as exc_info:
            ser.is_valid(raise_exception=True)

        assert "is_published" in exc_info.value.detail
        assert exc_info.value.detail["is_published"]

    def test_title_content_is_published_fields_can_be_updated(self, posts):
        post = posts["post_1"]

        data = {
            "title": "This is the latest title update",
            "content": "This is the latest content update",
            "is_published": False,
        }

        ser = PostDetailSerializer(instance=post, data=data, partial=True)
        ser.is_valid()
        ser.save()

        post.refresh_from_db()

        assert post.title == data["title"]
        assert post.content == data["content"]
        assert post.is_published == data["is_published"]

    def test_read_only_fields(self, posts):
        ser = PostDetailSerializer()
        writable_fields = {
            name for name, field in ser.fields.items() if not field.read_only
        }

        assert writable_fields == {"content", "is_published", "title"}

    def test_read_only_fields_cannot_be_updated(self, posts):
        post = Post.objects.first()
        user = get_user_model().objects.first()

        old_id = post.id
        old_author = post.author
        old_created_at = post.created_at
        old_likes = post.like_count = 10
        old_top_comments = post.top_comments = []
        old_comment_count = post.comment_count = 3
        data = {
            "id": "898393",
            "author": user,
            "created_at": "05-01-2026",
            "likes": 23,
            "top_comments": [],
            "comment_count": 12,
        }

        ser = PostDetailSerializer(instance=post, data=data)
        ser.is_valid()

        assert post.id == old_id
        assert post.author == old_author
        assert post.created_at == old_created_at
        assert post.like_count == old_likes
        assert post.top_comments == old_top_comments
        assert post.comment_count == old_comment_count

    def test_likes_maps_to_like_count(self, posts):
        post = posts["post_2"]
        post.like_count = 932

        ser = PostDetailSerializer(instance=post)

        assert ser.data["likes"] == 932

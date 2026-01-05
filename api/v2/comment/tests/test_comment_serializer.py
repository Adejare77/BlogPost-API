from api.v2.comment.serializer import (
    CommentCreateSerializer,
    CommentDetailSerializer,
    CommentListSerializer,
    ReplyCreateSerializer,
    ReplyDetailSerializer,
    ReplyListSerializer,
)

from rest_framework import serializers
from django.contrib.auth import get_user_model
from app.comment.models import Comment
import pytest


class TestCommentCreateSerializer:
    def test_valid_data_validates_successfully(self):
        data = {"content": "Valid Comment"}

        serializer = CommentCreateSerializer(data=data)
        assert serializer.is_valid() is True

    def test_missing_content_fails_validation(self):
        data = {}

        serializer = CommentCreateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_empty_content_fails_validation(self):
        data = {"content": ""}

        serializer = CommentCreateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_serialization_includes_expected_fields(self, users, posts):
        user = users["user_1"]
        post = posts["post_1"]
        data = {"content": "Valid Comment"}

        serializer = CommentCreateSerializer(data=data)
        assert serializer.is_valid() is True

        comment = serializer.save(author=user, post=post)
        expected_fields = {"id", "author", "post", "content", "created_at"}
        assert expected_fields.issubset({f.name for f in comment._meta.get_fields()})


class TestCommentListSerializer:
    def test_serialization_includes_expected_fields(self, comments):

        ser = CommentListSerializer(instance=comments["comment_1"])
        expected_field = [
            "id",
            "author",
            "post_id",
            "excerpt",
            "reply_count",
            "likes",
            "created_at",
        ]

        assert expected_field == ser.Meta.fields

    def test_serialization_fields_are_read_only(self, comments):
        ser = CommentListSerializer(instance=comments["comment_1"])

        write_fields = {
            name for name, field in ser.fields.items() if not field.read_only
        }

        assert write_fields == set()


class TestCommentDetailSerializer:
    def tests_serialization_includes_expected_fields(self, comments):
        expected_fields = {
            "id",
            "author",
            "post_id",
            "content",
            "top_replies",
            "reply_count",
            "likes",
            "created_at",
        }
        ser = CommentDetailSerializer(instance=comments["comment_2"])

        assert expected_fields == set(ser.Meta.fields)

    def test_empty_content_cannot_be_updated(self, comments):
        comment = comments["comment_1"]
        data = {"content": ""}
        ser = CommentDetailSerializer(instance=comment, data=data)

        with pytest.raises(serializers.ValidationError) as exc_info:
            ser.is_valid(raise_exception=True)

        assert "content" in exc_info.value.detail
        assert "content field cannot be empty" in exc_info.value.detail["content"]

    def test_valid_content_field_can_be_updated(self, comments):
        comment = comments["comment_1"]
        data = {"content": "Valid comment"}
        ser = CommentDetailSerializer(instance=comment, data=data)
        ser.is_valid()
        ser.save()

        comment.refresh_from_db()
        assert comment.content == data["content"]

    def test_serialization_read_only_fields(self, comments):
        ser = CommentDetailSerializer()

        writable_fields = {
            name for name, field in ser.fields.items() if not field.read_only
        }

        assert writable_fields == {"content"}

    def test_read_only_fields_cannot_be_updated(self, users, posts, comments):
        comment = comments["comment_1"]
        original_values = {
            "id": comment.id,
            "author_id": comment.author_id,
            "post_id": comment.post_id,
            "created_at": comment.created_at,
        }
        data = {
            "id": "23439348",
            "author": users["user_1"].id,
            "post": posts["post_1"].id,
            "top_replies": [],
            "reply_count": 999,
            "likes": 9999,
            "created_at": "2027-01-11",
            "content": "Valid Updated Content",
        }

        ser = CommentDetailSerializer(instance=comment, data=data, partial=True)

        assert ser.is_valid(), ser.errors
        ser.save()

        comment.refresh_from_db()

        # Read-only fields remain constant
        assert comment.id == original_values["id"]
        assert comment.post_id == original_values["post_id"]
        assert comment.author_id == original_values["author_id"]
        assert comment.created_at == original_values["created_at"]

        # Write field change
        assert comment.content == data["content"]

    def test_likes_maps_to_like_count(self, comments):
        comment = comments["comment_5"]
        comment.like_count = 323  # mock likes

        ser = CommentDetailSerializer(instance=comment)
        assert ser.data["likes"] == 323


class TestReplyCreateSerializer:
    def test_valid_data_validates_successfully(self):
        data = {"content": "Valid reply"}

        ser = ReplyCreateSerializer(data=data)
        assert ser.is_valid(), ser.errors

    def test_missing_content_fails_validation(self):
        data = {}

        serializer = ReplyCreateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_empty_content_fails_validation(self):
        data = {"content": ""}

        serializer = ReplyCreateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_serialization_includes_expected_fields(self, users, posts):
        user = users["user_1"]
        post = posts["post_1"]
        data = {"content": "Valid reply"}

        serializer = ReplyCreateSerializer(data=data)
        assert serializer.is_valid() is True

        comment = serializer.save(author=user, post=post)
        expected_fields = {"id", "author", "post", "content", "created_at"}
        assert expected_fields.issubset({f.name for f in comment._meta.get_fields()})


class TestReplyListSerializer:
    def test_serialization_includes_expected_fields(self, comments):

        ser = ReplyListSerializer(instance=comments["comment_1"])
        expected_field = {"id", "author", "excerpt", "likes", "created_at"}

        assert expected_field == set(ser.Meta.fields)

    def test_serialization_fields_are_read_only(self, comments):
        ser = ReplyListSerializer(instance=comments["comment_1"])

        write_fields = {
            name for name, field in ser.fields.items() if not field.read_only
        }

        assert write_fields == set()


class TestReplyDetailSerializer:
    def tests_serialization_includes_expected_fields(self, comments):
        expected_fields = {"id", "author", "content", "parent", "likes", "created_at"}
        ser = ReplyDetailSerializer(instance=comments["comment_2"])

        assert expected_fields == set(ser.Meta.fields)

    def test_empty_content_cannot_be_updated(self, comments):
        comment = comments["comment_1"]
        data = {"content": ""}
        ser = ReplyDetailSerializer(instance=comment, data=data)

        with pytest.raises(serializers.ValidationError) as exc_info:
            ser.is_valid(raise_exception=True)

        assert "content" in exc_info.value.detail
        assert "content field cannot be empty" in exc_info.value.detail["content"]

    def test_valid_content_field_can_be_updated(self, comments):
        comment = comments["comment_1"]
        data = {"content": "Valid reply"}
        ser = ReplyDetailSerializer(instance=comment, data=data)
        ser.is_valid()
        ser.save()

        comment.refresh_from_db()
        assert comment.content == data["content"]

    def test_serialization_read_only_fields(self, comments):
        ser = ReplyDetailSerializer()

        writable_fields = {
            name for name, field in ser.fields.items() if not field.read_only
        }

        assert writable_fields == {"content"}

    def test_read_only_fields_cannot_be_updated(self, users, posts, comments):
        comment = comments["comment_1"]
        original_values = {
            "id": comment.id,
            "author_id": comment.author_id,
            "post_id": comment.post_id,
            "created_at": comment.created_at,
        }
        data = {
            "id": "23439348",
            "author": users["user_1"].id,
            "post": posts["post_1"].id,
            "top_replies": [],
            "reply_count": 999,
            "likes": 9999,
            "created_at": "2027-01-11",
            "content": "Valid Updated Content",
        }

        ser = ReplyDetailSerializer(instance=comment, data=data, partial=True)

        assert ser.is_valid(), ser.errors
        ser.save()

        comment.refresh_from_db()

        # Read-only fields remain constant
        assert comment.id == original_values["id"]
        assert comment.post_id == original_values["post_id"]
        assert comment.author_id == original_values["author_id"]
        assert comment.created_at == original_values["created_at"]

        # Write field change
        assert comment.content == data["content"]

    def test_likes_maps_to_like_count(self, comments):
        comment = comments["comment_5"]
        comment.like_count = 323  # mock likes

        ser = ReplyDetailSerializer(instance=comment)

        assert ser.data["likes"] == 323

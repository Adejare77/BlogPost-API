from api.v2.comment.serializer import (
    CommentCreateSerializer,
    CommentDetailSerializer,
    CommentListSerializer,
    ReplyCreateSerializer,
    ReplyDetailSerializer,
    ReplyListSerializer
)

from rest_framework import serializers
from django.contrib.auth import get_user_model
from app.comment.models import Comment

class TestCommentCreateSerializer:
    def test_valid_data_validates_successfully(self):
        data = {
            'content': 'Valid Comment'
        }

        serializer = CommentCreateSerializer(data=data)
        assert serializer.is_valid() is True

    def test_missing_content_fails_validation(self):
        data = {}

        serializer = CommentCreateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_empty_content_fails_validation(self):
        data = {'content': ''}

        serializer = CommentCreateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_serialization_includes_expected_fields(self, users, posts):
        user = users['user_1']
        post = posts['post_1']
        data = {
            'content': 'Valid Comment'
        }

        serializer = CommentCreateSerializer(data=data)
        assert serializer.is_valid() is True

        comment = serializer.save(author=user, post=post)

        expected_fields = {
            'id', 'author', 'post_id', 'content', 'created_at'
        }

        assert expected_fields == {f.name for f in comment._meta.get_fields()}



class TestCommentListSerializer:
    def test_no_n_plus_one_queries(self, posts, comments, django_assert_num_queries):
        post = posts['post_1']
        comments = Comment.objects.filter()

    def test_serialization_includes_expected_fields(self):
        pass

    def test_serialization_fields_are_read_only(self):
        pass

class TestCommentDetailSerializer:
    def tests_serialization_includes_expected_fields(self):
        pass

    def test_empty_content_cannot_be_updated(self):
        pass

    def test_valid_content_field_can_be_updated(self):
        pass

    def test_serialization_read_only_fields(self):
        pass

    def test_read_only_fields_cannot_be_updated(self):
        pass

    def test_likes_maps_to_like_count(self):
        pass

from typing import Dict

from rest_framework import serializers

from app.comment.models import Comment
from app.post.models import Post
from django.utils.text import Truncator


class PostListSerializer(serializers.ModelSerializer):
    comment_count = serializers.IntegerField(read_only=True)
    likes = serializers.IntegerField(read_only=True, source="like_count")
    excerpt = serializers.SerializerMethodField()

    def get_excerpt(self, obj):
        words = obj.content.split()
        if len(words) <= 30:
            return obj.content
        return Truncator(obj.content).words(30, truncate=" ...")

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "title",
            "excerpt",
            "likes",
            "comment_count",
            "is_published",
            "created_at",
        ]
        read_only_fields = fields


class PostCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        error_messages={
            "blank": "title field cannot be empty",
            "required": "title field is required"
            }
    )
    content = serializers.CharField(
        error_messages={
            "blank": "content field cannot be empty",
            "required": "content field is required"
            }
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "title",
            "content",
            "is_published",
            "created_at",
        ]
        read_only_fields = ['id', 'author', 'created_at']

    def create(self, validated_data: Dict[str, str]):
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data: Dict[str, str]):
        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.save()
        return instance

class TopCommentListSerializer(serializers.ModelSerializer):
    excerpt = serializers.SerializerMethodField()
    likes = serializers.IntegerField(read_only=True, source='like_count')
    reply_count = serializers.IntegerField(read_only=True)

    def get_excerpt(self, obj):
        if not obj.content:
            return ""
        word = obj.content.split()
        if len(word) <= 10:
            return obj.content
        return Truncator(obj.content).words(10, truncate=" ...")

    class Meta:
        model = Comment
        fields = ['id', 'author', 'excerpt', 'likes', 'reply_count', 'created_at']
        read_only_fields = fields


class PostDetailSerializer(serializers.ModelSerializer):
    top_comments = TopCommentListSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    likes = serializers.IntegerField(read_only=True, source="like_count")
    content = serializers.CharField(error_messages={
        "blank": "content field cannot be empty"
    })
    title = serializers.CharField(error_messages={
        "blank": "title field cannot be empty"
    })
    title = serializers.CharField(
        required=False,
        allow_blank=True,
        error_messages={
        "blank": "title field cannot be empty"
    })

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "title",
            "content",
            "is_published",
            "likes",
            "comment_count",
            "top_comments",
            "created_at",
        ]
        read_only_fields = [
            'id', 'author', 'created_at', 'likes', 'comment_count', 'top_comments'
        ]

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.save()
        return instance

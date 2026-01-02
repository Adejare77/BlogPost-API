from typing import Dict

from rest_framework import serializers

from app.comment.models import Comment

from django.utils.text import Truncator


class CommentListSerializer(serializers.ModelSerializer):
    excerpt = serializers.SerializerMethodField()
    reply_count = serializers.IntegerField(read_only=True)
    likes = serializers.IntegerField(read_only=True, source="like_count")

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "post_id",
            "excerpt",
            "reply_count",
            "likes",
            "created_at",
        ]
        read_only_fields = fields

    def get_excerpt(self, obj):
        words = obj.content.split()
        if len(words) <= 30:
            return obj.content
        return Truncator(obj.content).words(30, truncate=" ...")

class CommentCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(error_messages={
        "required": "content field is required",
        "blank": "content field cannot be empty",
    })

    class Meta:
        model = Comment
        fields = [
            'id',
            'author',
            'post_id',
            'content',
            'created_at'
            ]
        read_only_fields = ['id', 'author', 'post_id', 'created_at']


    def create(self, validated_data: Dict[str, str]):
        return Comment.objects.create(**validated_data)

    # def update(self, instance, validated_data: Dict[str, str]):
    #     for k, v in validated_data.items():
    #         setattr(instance, k, v)

    #     instance.save()
    #     return instance

class ReplyListSerializer(serializers.ModelSerializer):
    excerpt = serializers.SerializerMethodField()
    likes = serializers.IntegerField(read_only=True, source="like_count")

    class Meta:
        model = Comment
        fields = ["id", "author", "excerpt", "likes", "created_at"]
        read_only_fields = fields

    def get_excerpt(self, obj):
        words = obj.content.split()
        if len(words) <= 20:
            return obj.content
        return Truncator(obj.content).words(30, truncate=" ...")


class CommentDetailSerializer(serializers.ModelSerializer):
    top_replies = ReplyListSerializer(many=True, read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    likes = serializers.IntegerField(read_only=True, source="like_count")

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "post_id",
            "content",
            "top_replies",
            "reply_count",
            "likes",
            "created_at",
        ]
        read_only_fields = ['id', 'author', 'post_id', 'top_replies', 'reply_count', 'likes', 'created_at']

    # def create(self, validated_data):
    #     return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data: Dict[str, str]):
        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.save()
        return instance

class ReplyCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(
        error_messages={
            "blank": "content field cannot be empty",
            "required": "content field is required",
        }
    )

    class Meta:
        model = Comment
        fields = [
            'id',
            'author',
            'content',
            'parent',
            'created_at'
            ]
        read_only_fields = ['id', 'author', 'parent', 'created_at']

    def create(self, validated_data: Dict[str, str]):
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data: Dict[str, str]):
        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.save()
        return instance


class ReplyDetailSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(read_only=True, source="like_count")

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "content",
            "parent",
            "likes",
            "created_at"
        ]
        read_only_fields = ['id', 'author', 'parent', 'likes', 'creaated_at']


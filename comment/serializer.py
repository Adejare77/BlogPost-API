from rest_framework import serializers
from comment.models import Comment
from post.models import Post
from typing import Dict

class CommentListSerializer(serializers.ModelSerializer):
    excerpt = serializers.CharField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'excerpt', 'reply_count', 'like_count', 'created_at']
        read_only_fields = fields


class ReplySummarySerializer(serializers.ModelSerializer):
    excerpt = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'excerpt', 'created_at']
        read_only_fields = fields


class CommentDetailSerializer(serializers.ModelSerializer):
    content = serializers.CharField(error_messages={"required": "content field is required"})
    top_replies = ReplySummarySerializer(many=True, read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'content', 'top_replies', 'reply_count', 'like_count', 'created_at']
        read_only_fields = ['id', 'author', 'post', 'created_at']

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data: Dict[str, str]):
        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.save()
        return instance


class ReplyListSerializer(serializers.ModelSerializer):
    excerpt = serializers.CharField(read_only=True)
    likes = serializers.IntegerField(read_only=True, source='like_count')

    class Meta:
        model = Comment
        fields = ['id', 'author', 'excerpt', 'likes', 'created_at']
        read_only_fields = fields


class ReplyDetailSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'parent', 'like_count', 'created_at']
        read_only_fields = ['id', 'author', 'parent', 'created_at']

    def create(self, validated_data: Dict[str, str]):
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data: Dict[str, str]):
        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.save()
        return instance

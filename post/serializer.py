from rest_framework import serializers
from post.models import Post
from comment.models import Comment
from typing import Dict


class CommentSummarySerializer(serializers.ModelSerializer):
    excerpt = serializers.CharField(read_only=True)
    likes = serializers.IntegerField(read_only=True, source='like_count')
    reply_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'excerpt', 'likes', 'reply_count', 'created_at']
        read_only_fields = fields


class PostDetailSerializer(serializers.ModelSerializer):
    top_comments = CommentSummarySerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    likes = serializers.IntegerField(read_only=True, source='like_count')

    class Meta:
        model = Post
        fields = ['isbn', 'author', 'title', 'content', 'is_published', 'likes', 'comment_count', 'top_comments', 'created_at']
        read_only_fields = ['isbn', 'author', 'created_at']

    def create(self, validated_data: Dict[str, str]):
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data: Dict[str, str]):
        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.save()
        return instance


class PostListSerializer(serializers.ModelSerializer):
    comment_count = serializers.IntegerField(read_only=True)
    likes = serializers.IntegerField(read_only=True, source='like_count')
    excerpt = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        fields = ['isbn', 'title', 'excerpt', 'author', 'likes', 'comment_count', 'is_published', 'created_at']

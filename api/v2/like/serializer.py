from rest_framework import serializers

from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

from app.like.models import Like
from app.post.models import Post
from app.comment.models import Comment


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "content_type", "user"]
        read_only_fields = fields

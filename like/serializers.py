from rest_framework import serializers

from like.models import Like


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "content_type", "user"]
        read_only_fields = fields

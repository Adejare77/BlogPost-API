import uuid
from django.db import models
from post.models import Post
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from like.models import Like


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(
        blank=False,
        null=False,
        error_messages={"blank": "content field cannot be empty"}
    )
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = GenericRelation(Like, related_query_name='likes')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

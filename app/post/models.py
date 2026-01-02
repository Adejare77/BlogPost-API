import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from app.like.models import Like


# Create your models here.
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        error_messages={"required": "author field is required"},
    )
    title = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        error_messages={
            "blank": "title field cannot be empty",
            "max_length": "cannot accept more than 50 characters",
        },
    )
    content = models.TextField(
        blank=False,
        null=False,
        error_messages={
            "blank": "content field cannot be empty",
        },
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Polymorhpic Relation with Like. Reverse relation with child
    likes = GenericRelation(Like, related_query_name="likes")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.author.full_name

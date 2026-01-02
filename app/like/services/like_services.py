from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from app.like.models import Like


class LikeService:
    @staticmethod
    def like_object(user, model_object, object_id):
        content_type = ContentType.objects.get_for_model(model_object)
        obj = model_object.objects.filter(id=object_id).first()

        if not obj:
            return None, status.HTTP_404_NOT_FOUND

        like, created = Like.objects.get_or_create(
            object_id=object_id,
            user=user,
            content_type=content_type
        )

        if not created:
            return None, status.HTTP_400_BAD_REQUEST

        return like, status.HTTP_201_CREATED

    @staticmethod
    def unlike_object(user, model_object, object_id):
        content_type = ContentType.objects.get_for_model(model_object)

        obj = model_object.objects.filter(id=object_id).first()
        if not obj:
            return status.HTTP_404_NOT_FOUND, True

        like = Like.objects.filter(user=user, object_id=object_id, content_type=content_type).first()
        if not like:
            return status.HTTP_404_NOT_FOUND, False

        like.delete()
        return status.HTTP_204_NO_CONTENT, False


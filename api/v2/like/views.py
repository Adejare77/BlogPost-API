from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from api.v2.like.serializer import LikeSerializer
from rest_framework.response import Response
from app.core.permissions import IsAuthenticated
from app.comment.models import Comment
from app.post.models import Post
from app.like.services.like_services import LikeService


class LikePostAPIView(APIView):
    """
    POST -> create: like a post
    DELETE -> like: delete a liked post
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        like, status_code = LikeService.like_object(
            user=request.user,
            model_object=Post,
            object_id=post_id
        )

        if status_code == status.HTTP_404_NOT_FOUND:
            raise NotFound("Post not found")
        elif status_code == status.HTTP_400_BAD_REQUEST:
            raise ValidationError("Post already liked")

        ser = LikeSerializer(instance=like)
        return Response(ser.data, status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        status_code, err = LikeService.unlike_object(
            user=request.user,
            model_object=Post,
            object_id=post_id
        )

        if status_code == status.HTTP_404_NOT_FOUND:
            raise NotFound("Post not found" if err else "Like not found")

        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeCommentAPIView(APIView):
    """
    POST -> like: comments
    DELETE -> like: delete a liked comments
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        like, status_code = LikeService.like_object(
            user=request.user,
            model_object=Comment,
            object_id=comment_id
        )
        if status_code == status.HTTP_404_NOT_FOUND:
            raise NotFound("Comment not found")

        elif status_code == status.HTTP_400_BAD_REQUEST:
            raise ValidationError("Comment already liked")

        ser = LikeSerializer(instance=like)
        return Response(ser.data, status=status.HTTP_201_CREATED)

    def delete(self, request, comment_id):
        status_code, err = LikeService.unlike_object(
            user = request.user,
            model_object=Comment,
            object_id=comment_id
        )

        if status_code == status.HTTP_404_NOT_FOUND:
            return NotFound("Comment not found" if err else "like not found")

        return Response(status=status.HTTP_204_NO_CONTENT)

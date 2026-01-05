from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from app.core.permissions import IsAuthenticated
from app.comment.models import Comment
from app.post.models import Post
from app.like.models import Like
from django.contrib.contenttypes.models import ContentType


class LikePostAPIView(APIView):
    """
    POST -> create: like a post
    DELETE -> like: delete a liked post
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("Post not found.")

        content_type = ContentType.objects.get_for_model(Post)

        _, created = Like.objects.get_or_create(
            user=request.user, object_id=post_id, content_type=content_type
        )
        return Response(
            {"liked": created, "like_count": post.likes.count()},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("Post not found.")

        content_type = ContentType.objects.get_for_model(Post)

        deleted_count, _ = Like.objects.filter(
            user=request.user, object_id=post_id, content_type=content_type
        ).delete()

        return Response(
            {"liked": deleted_count > 0, "like_count": post.likes.count()},
            status=status.HTTP_200_OK,
        )


class LikeCommentAPIView(APIView):
    """
    POST -> like: comments
    DELETE -> like: delete a liked comments
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        try:
            post = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            raise NotFound("Comment not found.")

        content_type = ContentType.objects.get_for_model(Comment)

        _, created = Like.objects.get_or_create(
            user=request.user, object_id=comment_id, content_type=content_type
        )
        return Response(
            {"liked": created, "like_count": post.likes.count()},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            raise NotFound("Comment not found.")

        content_type = ContentType.objects.get_for_model(Comment)

        deleted_count, _ = Like.objects.filter(
            user=request.user, object_id=comment_id, content_type=content_type
        ).delete()

        return Response(
            {"liked": deleted_count > 0, "like_count": comment.likes.count()},
            status=status.HTTP_200_OK,
        )

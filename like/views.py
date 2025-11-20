from rest_framework.decorators import api_view, permission_classes
from core.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from like.models import Like
from django.contrib.contenttypes.models import ContentType
from like.serializers import LikeSerializer
from post.models import Post
from comment.models import Comment



@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def like_post(request: Request, post_id):
    """
    Like (POST) or unlike (DELETE) a Post.
    """
    try:
        Post.objects.get(isbn=post_id)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    content_type = ContentType.objects.get_for_model(Post)

    if request.method == 'POST':
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=post_id
        )

        if not created:
            return Response({"detail": "Post already liked"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LikeSerializer(instance=like)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    try:
        like = Like.objects.get(
            object_id=post_id,
            user=request.user,
            content_type=content_type
        )
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    except Like.DoesNotExist:
        return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def like_comment(request: Request, comment_id):
    """
    Like (POST) or unlike (DELETE) a Comment.
    """
    try:
        Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    content_type = ContentType.objects.get_for_model(Comment)

    if request.method == 'POST':
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=comment_id
        )

        if not created:
            return Response({"detail": "Comment already liked"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LikeSerializer(instance=like)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    try:
        like = Like.objects.get(
            object_id=comment_id,
            user=request.user,
            content_type=content_type
        )
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    except Like.DoesNotExist:
        return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)


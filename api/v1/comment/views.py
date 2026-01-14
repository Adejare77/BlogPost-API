from django.db.models import Count, Prefetch, Value
from django.db.models.functions import Concat, Substr
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.comment.serializer import (
    CommentDetailSerializer,
    CommentListSerializer,
    ReplyDetailSerializer,
    ReplyListSerializer,
)
from app.comment.models import Comment
from app.core.permissions import AllowAnyForGetRequireAuthForWrite, IsAdminOrSelf
from app.post.models import Post


@api_view(["GET", "POST"])
@permission_classes([AllowAnyForGetRequireAuthForWrite])
def post_comments(request: Request, post_id):
    try:
        post = Post.objects.get(id=post_id, is_published=True)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        queryset = (
            Comment.objects.filter(post=post_id, parent__isnull=True)
            .annotate(
                excerpt=Concat(Substr("content", 1, 80), Value("...")),
                reply_count=Count("replies__id", distinct=True),
                like_count=Count("likes__id", distinct=True),
            )
            .order_by("-like_count", "-reply_count")
        )

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(request=request, queryset=queryset)
        serializer = CommentListSerializer(instance=page, many=True)

        return paginator.get_paginated_response(serializer.data)

    serializer = CommentDetailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(post=post, author=request.user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([AllowAnyForGetRequireAuthForWrite])
def post_comment_detail(request: Request, comment_id):
    if request.method == "GET":
        try:
            Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found"})
        replies_qs = (
            Comment.objects.filter(parent=comment_id)
            .annotate(excerpt=(Concat(Substr("content", 1, 50), Value("..."))))
            .order_by("-likes")[:3]
        )

        qs = (
            Comment.objects.prefetch_related(
                Prefetch("replies", queryset=replies_qs, to_attr="top_replies")
            )
            .annotate(
                reply_count=Count("replies", distinct=True),
                like_count=Count("likes__id", distinct=True),
            )
            .get(id=comment_id)
        )

        serializer = CommentDetailSerializer(instance=qs)
        return Response(serializer.data)

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response(
            {"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
        )

    permission = IsAdminOrSelf()
    if not permission.has_object_permission(request, None, comment):
        raise PermissionDenied(permission.message)

    if request.method == "PATCH":
        serializer = CommentDetailSerializer(
            instance=comment, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([AllowAnyForGetRequireAuthForWrite])
def comment_replies(request: Request, comment_id):
    if request.method == "GET":
        queryset = (
            Comment.objects.filter(parent=comment_id)
            .annotate(
                excerpt=Concat(Substr("content", 1, 50), Value("...")),
                like_count=Count("likes__id", distinct=True),
            )
            .order_by("-like_count")
        )

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(request=request, queryset=queryset)

        serializer = ReplyListSerializer(instance=page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # ensures replies are only to comment not replies
    try:
        comment = Comment.objects.get(id=comment_id, parent__isnull=True)
    except Comment.DoesNotExist:
        return Response({"detail": "Comment not found"})

    serializer = ReplyDetailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(author=request.user, parent=comment, post=comment.post)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([AllowAnyForGetRequireAuthForWrite])
def comment_reply_details(request: Request, reply_id):
    if request.method == "GET":
        try:
            qs_reply = Comment.objects.annotate(
                like_count=Count("likes__id", distinct=True)
            ).get(id=reply_id)
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Reply not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReplyDetailSerializer(instance=qs_reply)
        return Response(serializer.data, status=status.HTTP_200_OK)

    try:
        reply = Comment.objects.get(parent__isnull=False, id=reply_id)
    except Comment.DoesNotExist:
        return Response({"detail": "Reply not found"}, status=status.HTTP_404_NOT_FOUND)

    permission = IsAdminOrSelf()
    if not permission.has_object_permission(request, None, reply):
        raise PermissionDenied(permission.message)
    if request.method == "PATCH":
        serializer = ReplyDetailSerializer(
            instance=reply, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, post=reply.post, parent=reply.parent)

        return Response(serializer.data, status=status.HTTP_200_OK)

    reply.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

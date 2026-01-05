from django.db.models import Count, Prefetch, Value, Q
from django.db.models.functions import Concat, Substr
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

from app.comment.models import Comment
from app.core.permissions import (
    AllowAnyForGetRequireAuthForWrite,
    IsAdminOrSelf,
    DraftAccessPermission,
)
from app.post.filters import PostFilter
from app.post.models import Post
from api.v1.post.serializer import PostDetailSerializer, PostListSerializer
from app.post.service import get_accessible_posts_queryset


@extend_schema(operation_id="ListPosts")
@api_view(["POST", "GET"])
@permission_classes([AllowAnyForGetRequireAuthForWrite])
def post_list(request: Request):
    if request.method == "GET":
        qs = Post.objects.order_by("-created_at").annotate(
            comment_count=Count(
                "comments", filter=Q(comments__parent__isnull=True), distinct=True
            ),
            excerpt=Concat(Substr("content", 1, 100), Value(" ...")),
            like_count=Count("likes", distinct=True),
        )

        user = request.user
        query_params = request.query_params
        qs = get_accessible_posts_queryset(user, qs, query_params)

        filterset = PostFilter(data=query_params, request=request, queryset=qs)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        qs = filterset.qs  # filtered query set

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset=qs, request=request)

        serializer = PostListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = PostDetailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(author=request.user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(operation_id="RetrievePost")
@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([AllowAnyForGetRequireAuthForWrite])
def post_detail(request: Request, post_id):
    if request.method == "GET":
        try:
            top_comment_qs = (
                Comment.objects.filter(post=post_id)
                .prefetch_related("replies")
                .annotate(
                    excerpt=Concat(Substr("content", 1, 100), Value(" ...")),
                    like_count=Count("likes", distinct=True),
                    reply_count=Count("replies", distinct=True),
                )
                .order_by("-likes", "-reply_count")[:3]
            )

            post = (
                Post.objects.prefetch_related(
                    Prefetch(
                        "comments", queryset=top_comment_qs, to_attr="top_comments"
                    )
                )
                .annotate(
                    comment_count=Count(
                        "comments",
                        filter=Q(comments__parent__isnull=True),
                        distinct=True,
                    ),
                    like_count=Count("likes", distinct=True),
                )
                .get(id=post_id)
            )

            if post.is_published == False and not request.user.is_authenticated:
                raise NotAuthenticated("Authentication credentials were not provided.")

            permission = DraftAccessPermission()
            if not permission.has_object_permission(request, None, post):
                raise PermissionDenied(permission.message)

        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PostDetailSerializer(instance=post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    # check for permission
    permissions = IsAdminOrSelf()
    if not permissions.has_object_permission(request, None, post):
        raise PermissionDenied(permissions.message)

    if request.method == "PATCH":
        serializer = PostDetailSerializer(
            instance=post, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    post.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_popular_posts(request: Request):
    qs = (
        Post.objects.filter(is_published=True)
        .annotate(
            excerpt=Concat(Substr("content", 1, 100), Value("...")),
            like_count=Count("likes", distinct=True),
            comment_count=Count(
                "comments", filter=Q(comments__parent__isnull=True), distinct=True
            ),
        )
        .order_by("-like_count", "comment_count")[:10]
    )

    serializer = PostListSerializer(qs, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

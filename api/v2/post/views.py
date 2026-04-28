import logging

from django.db.models import Count, Prefetch, Q
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from api.v2.post.serializer import (
    PostCreateSerializer,
    PostDetailSerializer,
    PostListSerializer,
)
from app.comment.models import Comment
from app.core.permissions import (
    DraftAccessPermission,
    IsAdminOrSelf,
    IsAuthenticated,
    IsOwner,
)
from app.post.filters import PostFilter
from app.post.models import Post
from app.post.service import get_accessible_posts_queryset

logger = logging.getLogger("app")


class PostListCreateAPIView(ListCreateAPIView):
    """
    GET -> list: posts (with pagination)
    POST -> create: post
    """

    pagination_class = PageNumberPagination
    filterset_class = PostFilter

    def get_queryset(self):
        base_qs = (
            Post.objects.order_by("-created_at")
            .select_related("author")
            .annotate(
                like_count=Count("likes", distinct=True),
                comment_count=Count(
                    "comments", filter=Q(comments__parent__isnull=True), distinct=True
                ),
            )
        )

        user = self.request.user
        query_params = self.request.query_params
        base_qs = get_accessible_posts_queryset(user, base_qs, query_params)

        return base_qs

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny(), DraftAccessPermission()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        return (
            PostListSerializer if self.request.method == "GET" else PostCreateSerializer
        )

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)

        if post:
            logger.info(
                "Post created" if post.is_published else "Draft created",
                extra={
                    "user_id": self.request.user.id,
                    "post_id": post.id,
                    "title": post.title,
                    "request_id": self.request.headers.get("X-requested-ID"),
                },
            )


class PostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    GET -> post: retrieve
    PATCH -> post: update
    DELETE -> post: destroy
    """

    serializer_class = PostDetailSerializer
    filterset_class = PostFilter
    lookup_field = "id"
    lookup_url_kwarg = "post_id"

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny(), DraftAccessPermission()]
        elif self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdminOrSelf()]
        else:
            return [IsAuthenticated(), IsOwner()]

    def get_queryset(self):
        comments_qs = (
            Comment.objects.filter(post_id=self.kwargs["post_id"])
            .annotate(
                like_count=Count("likes", distinct=True), reply_count=Count("replies")
            )
            .order_by("-like_count", "-created_at")[:3]
        )

        return Post.objects.prefetch_related(
            Prefetch("comments", queryset=comments_qs, to_attr="top_comments")
        ).annotate(
            like_count=Count("likes", distinct=True),
            comment_count=Count("comments", distinct=True),
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(
            "Post updated" if instance.is_published else "Draft updated",
            extra={
                "user_id": self.request.user.id,
                "post_id": instance.id,
                "title": instance.title,
                "request_id": self.request.headers.get("X-requested-ID"),
            },
        )

    def perform_destroy(self, instance):
        logger.info(
            "Post deleted" if instance.is_published else "Draft deleted",
            extra={
                "user_id": self.request.user.id,
                "post_id": instance.id,
                "request_id": self.request.headers.get("X-requested-ID"),
            },
        )
        super().perform_destroy(instance)


class PopularPostListAPIView(ListAPIView):
    """
    GET -> list popular posts by likes and created_at
    """

    serializer_class = PostListSerializer
    permission_classes = [AllowAny]

    queryset = Post.objects.annotate(
        like_count=Count("likes", distinct=True),
        comment_count=Count(
            "comments", filter=Q(comments__parent__isnull=True), distinct=True
        ),
    ).order_by("-like_count", "-created_at")[:10]

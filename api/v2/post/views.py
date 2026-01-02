from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView
)
from api.v2.post.serializer import (
    PostCreateSerializer,
    PostListSerializer,
    PostDetailSerializer
)
from app.comment.models import Comment
from app.post.models import Post
from rest_framework.pagination import PageNumberPagination
from app.post.filters import PostFilter
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser
from django.db.models import Count, Q, Prefetch
from app.core.permissions import (
    IsAuthenticated,
    IsAdminOrSelf,
    IsOwner,
    DraftAccessPermission
)
from app.post.service import get_accessible_posts_queryset

class PostListCreateAPIView(ListCreateAPIView):
    """
    GET -> list: post (with pagination)
    POST -> create: post
    """
    pagination_class = PageNumberPagination
    filterset_class = PostFilter

    def get_queryset(self):
        base_qs = (
            Post.objects
            .order_by('-created_at')
            .annotate(
                like_count=Count("likes", distinct=True),
                comment_count=Count(
                    "comments",
                    filter=Q(comments__parent__isnull=True),
                    distinct=True
                )
            )
        )

        user = self.request.user
        query_params = self.request.query_params
        base_qs = get_accessible_posts_queryset(user, base_qs, query_params)

        return base_qs

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny(), DraftAccessPermission()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        return PostListSerializer if self.request.method == 'GET' else PostCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    GET -> post: retrieve
    PATCH -> post: update
    DELETE -> post: destroy
    """

    serializer_class = PostDetailSerializer
    filterset_class = PostFilter
    lookup_field = 'id'
    lookup_url_kwarg='post_id'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny(), DraftAccessPermission()]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated(), IsAdminOrSelf()]
        else:
            return [IsAuthenticated(), IsOwner()]

    def get_queryset(self):
        comments_qs = (
            Comment.objects
            .filter(post_id=self.kwargs["post_id"])
            .annotate(
                like_count=Count("likes", distinct=True),
                reply_count=Count("replies")
            )
            .order_by('-like_count', '-created_at')[:3]
        )

        return (
            Post.objects
            .prefetch_related(
                Prefetch("comments", queryset=comments_qs, to_attr='top_comments')
            )
            .annotate(
                like_count=Count("likes", distinct=True),
                comment_count=Count('comments', distinct=True)
            )
        )

class PopularPostListAPIView(ListAPIView):
    """
    GET -> list popular posts by likes and created_at
    """
    serializer_class = PostListSerializer
    permission_classes = [AllowAny]

    queryset = (
        Post.objects
        .annotate(
            like_count=Count("likes", distinct=True),
            comment_count=Count(
                "comments",
                filter=Q(comments__parent__isnull=True),
                distinct=True)
        )
        .order_by("-like_count", "-created_at")[:10]
    )

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.exceptions import NotFound
from app.comment.models import Comment
from app.post.models import Post
from django.db.models import Count, Prefetch
from rest_framework.permissions import AllowAny
from app.core.permissions import IsAdminOrSelf, IsAuthenticated, IsOwner
from rest_framework.pagination import PageNumberPagination
from api.v2.comment.serializer import (
    CommentCreateSerializer,
    CommentDetailSerializer,
    CommentListSerializer,
    ReplyCreateSerializer,
    ReplyListSerializer,
    ReplyDetailSerializer
)

class CommentListCreateAPIView(ListCreateAPIView):
    """
    GET -> List: comments (with pagination)
    POST -> Create: comment
    """
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        post = Post.objects.filter(id=self.kwargs['post_id']).first()
        if not post:
            raise NotFound("Post not found.")
        return (
            Comment.objects.filter(post=post, parent__isnull=True)
            .annotate(
                like_count=Count("likes", distinct=True),
                reply_count=Count("replies", distinct=True)
            )
            .order_by('-like_count', '-reply_count', '-created_at')
            )

    def get_serializer_class(self):
        return CommentListSerializer if self.request.method == 'GET' else CommentCreateSerializer

    def perform_create(self, serializer):
        try:
            post = Post.objects.get(id=self.kwargs['post_id'])
        except Post.DoesNotExist:
            raise NotFound("Post not found.")

        serializer.save(post=post, author=self.request.user)


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    GET -> retrieve: comment
    PATCH -> partial update: comment
    DELETE -> delete: comment
    """
    serializer_class = CommentDetailSerializer
    queryset = Comment.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "comment_id"

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsAdminOrSelf()]
        return [IsAuthenticated(), IsOwner()]


    def get_queryset(self):
        comment = Comment.objects.filter(id=self.kwargs['comment_id']).first()
        if not comment:
            raise NotFound("Comment not found.")
        replies_qs = (
            Comment.objects
            .filter(parent=comment)
            .annotate(like_count=Count("likes", distinct=True))
            .order_by("-likes", "-created_at")[:3]
        )
        return (
            Comment.objects.
            prefetch_related(
                Prefetch("replies", queryset=replies_qs, to_attr="top_replies")
            )
            .annotate(
                reply_count=Count("replies", distinct=True),
                like_count=Count("likes", distinct=True)
            )
            .filter(id=self.kwargs['comment_id'])
        )


class ReplyListCreateAPIView(ListCreateAPIView):
    """
    GET -> List: replies (with pagination)
    POST -> Create: reply
    """
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        return ReplyListSerializer if self.request.method == 'GET' else ReplyCreateSerializer

    def get_queryset(self):
        comment = Comment.objects.filter(id=self.kwargs['comment_id']).first()
        if not comment:
            raise NotFound("Comment not found.")
        return (
            Comment.objects
            .filter(parent=comment)
            .annotate(
                like_count=Count("likes", distinct=True)
            )
            .order_by("-like_count", "-created_at")
        )

    def perform_create(self, serializer):
        parent_comment = (
            Comment.objects
            .filter(id=self.kwargs['comment_id'], parent__isnull=True)
            .first()
        )
        if not parent_comment:
            raise NotFound("Comment not found.")
        serializer.save(
            author=self.request.user,
            post=parent_comment.post,
            parent=parent_comment
            )

class ReplyRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    GET -> retrieve: reply
    PATCH -> update: reply
    DELETE -> destroy: reply
    """

    serializer_class = ReplyDetailSerializer
    lookup_field = 'id'
    lookup_url_kwarg='reply_id'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsAdminOrSelf()]
        return [IsAuthenticated(), IsOwner()]

    def get_queryset(self):
        return (
            Comment.objects
            .annotate(like_count=Count("likes", distinct=True))
            .filter(id=self.kwargs['reply_id'])
        )



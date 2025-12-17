from django_filters import rest_framework as filters
from rest_framework.exceptions import PermissionDenied

from app.core.permissions import IsAuthenticated
from app.post.models import Post


class PostFilter(filters.FilterSet):
    author = filters.CharFilter(method="filter_author")
    status = filters.CharFilter(method="filter_status")

    class Meta:
        model = Post
        fields = ["status", "author"]

    def filter_status(self, queryset, name, value):
        if value.lower() not in ("draft", "all"):
            return queryset.filter(is_published=True)

        IsAuthenticated().has_permission(self.request, None)
        # for staffs
        if self.request.user.is_staff:
            return (
                queryset
                if value.lower() == "all"
                else queryset.filter(is_published=False)
            )

        # for non staff
        author = self.request.query_params.get("author")
        if author:  # author filter will take care of it
            return (
                queryset
                if value.lower() == "all"
                else queryset.filter(is_published=False)
            )
        else:  # if author is not given, default to current user
            return (
                queryset.filter(author=self.request.user)
                if value.lower() == "all"
                else queryset.filter(is_published=False, author=self.request.user)
            )

    def filter_author(self, queryset, name, value):
        if value == "me":
            IsAuthenticated().has_permission(self.request, None)
            return queryset.filter(author=self.request.user)

        # status = 'published' is given by default in view
        status = self.data.get("status")
        if status.lower() == "published":
            return queryset.filter(author__full_name__icontains=value)

        # for staffs
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset.filter(author__full_name__icontains=value)

        raise PermissionDenied("You do not have permission to perform this action")

from django_filters import rest_framework as filters
from app.post.models import Post


class PostFilter(filters.FilterSet):
    author = filters.CharFilter(method="filter_author")
    status = filters.CharFilter(method="filter_status")

    class Meta:
        model = Post
        fields = ['author', 'is_published']

    def filter_status(self, queryset, name, value):
        value = value.strip().lower()
        if value == 'draft':
            return queryset.filter(is_published=False)
        if value == 'all':
            return queryset
        return queryset.filter(is_published=True)

    def filter_author(self, queryset, name, value):
        value = value.strip().lower()
        if value == 'me':
            return queryset.filter(author=self.request.user)
        return queryset.filter(author__full_name__icontains=value)


from django_filters import rest_framework as filters

from app.post.models import Post


class PostFilter(filters.FilterSet):
    STATUS_CHOICES = [
        ("draft", "Drafts only"),
        ("published", "Published posts only (default)"),
        ("all", "All posts (drafts and published posts)"),
    ]
    author = filters.CharFilter(method="filter_author")
    status = filters.ChoiceFilter(method="filter_status", choices=STATUS_CHOICES)

    class Meta:
        model = Post
        fields = ["author", "status"]

    def filter_status(self, queryset, name, value):
        value = value.strip().lower()
        if value == "draft":
            return queryset.filter(is_published=False)
        if value == "all":
            return queryset
        return queryset.filter(is_published=True)

    def filter_author(self, queryset, name, value):
        value = value.strip().lower()
        if value == "me":
            return queryset.filter(author=self.request.user)
        return queryset.filter(author__full_name__icontains=value)

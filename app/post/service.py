from rest_framework.exceptions import NotAuthenticated, PermissionDenied


def get_accessible_posts_queryset(user, base_qs, query_params):
    """
    Returns queryset containing ONLY posts the user can access.
    Raises exceptions for permission violations
    """
    authenticated = user.is_authenticated
    status = query_params.get("status")
    author = query_params.get("author")

    if authenticated and user.is_staff:
        return base_qs

    if not authenticated and author == "me":
        raise NotAuthenticated("Authentication credentials were not provided.")

    if not status:
        return base_qs.filter(is_published=True)

    if status.strip().lower() in ("all", "draft"):
        if not authenticated:
            raise NotAuthenticated("Authentication credentials were not provided.")

        if not author:
            return base_qs.filter(author=user)

        if author.strip().lower() != "me":
            raise PermissionDenied("You do not have permission to perform this action.")

    return base_qs

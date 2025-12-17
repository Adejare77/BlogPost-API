from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            raise AuthenticationFailed("Authentication credentials were not provided")

        if not request.user.is_active:
            raise AuthenticationFailed("User is disabled")

        return True


class IsAdminUser(BasePermission):
    message = "You do not have permission to perform this action"

    def has_permission(self, request, view):
        return bool(request.user.is_staff)


class IsAdminOrSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "author"):
            # only owner or staff if the obj is not staff (Post and Comment)
            if obj.author == request.user or (
                request.user.is_staff and not obj.author.is_staff
            ):
                return True

        # owner (both staff or clients)
        if hasattr(obj, "id"):
            if obj == request.user or (request.user.is_staff and not obj.is_staff):
                return True

        # staff try other staff or client try other
        raise PermissionDenied("You do not have permission to perform this action")


class AllowAnyForGetRequireAuthForWrite(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True

        if not (request.user and request.user.is_authenticated):
            raise AuthenticationFailed("Authentication credentials were not provided")

        if not (request.user and request.user.is_active):
            raise AuthenticationFailed("User is disabled")

        return True

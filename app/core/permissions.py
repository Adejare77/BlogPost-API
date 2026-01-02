from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if not user.is_active:
            self.message = "User is disabled"
            return False

        return True


class IsOwner(BasePermission):
    message = "You do not have permission to perform this action."

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAdminUser(BasePermission):
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_staff)


class IsAdminOrSelf(BasePermission):
    message = "You do not have permission to perform this action."

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if hasattr(obj, 'author'):
            if obj.author == request.user:
                return True

            return False

        if obj.id == request.user:
            return True

        return False


class AllowAnyForGetRequireAuthForWrite(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False
        return True


class DraftAccessPermission(BasePermission):
    message = "You do not have permission to perform this action."

    def has_object_permission(self, request, view, obj):
        if obj.is_published == True:
            return True

        user = request.user
        return user.is_staff or user == obj.author

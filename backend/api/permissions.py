from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsCurrentUserOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (obj.user == request.user or request.user.is_staff)


class IsBlockedUser(permissions.BasePermission):
    message = 'This user is blocked.'

    def has_permission(self, request, view):
        user = request.user
        return not user.is_blocked


class UserPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if (
            request.method in permissions.SAFE_METHODS
            or request.method == 'POST'
        ):
            return True
        return (request.user.is_authenticated and not request.user.is_blocked
                (request.user.is_superuser or request.user.is_current_user))

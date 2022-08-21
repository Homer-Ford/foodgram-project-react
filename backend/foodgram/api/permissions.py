from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """Разрешения для администратора или только чтения."""

    def has_permission(self, request, view):
        return (
            request.method
            in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class AdminAuthorPermission(permissions.BasePermission):
    """Разрешения для администратора и автора."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (obj.author == request.user)
            or request.user.is_admin
        )

from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, IsAdminUser

class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == 'admin' or request.user.is_superuser)
        )

class IsUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'user'
        )

class IsAdminOrReadOnly(IsAdminRole, IsUserRole):
    def has_permission(self, request, view):
        if (request.method in SAFE_METHODS) and IsUserRole.has_permission(self, request, view):
            return True
        return super().has_permission(request, view)
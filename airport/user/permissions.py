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
    message = "Your email is not verified."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role != "user":
            return False

        if not request.user.is_active:
            self.message = "Your email is not verified."
            return False

        return True

class IsCompletedProfile(permissions.BasePermission):
    message = "Complete your profile first."

    def has_permission(self, request, view):
        return request.user.is_profile_completed

class IsNotCompletedProfile(permissions.BasePermission):
    message = "Profile is already completed."

    def has_permission(self, request, view):
        return not request.user.is_profile_completed

class IsAdminOrReadOnly(IsAdminRole, IsUserRole):
    def has_permission(self, request, view):
        if (request.method in SAFE_METHODS) and IsUserRole.has_permission(self, request, view):
            return True
        return super().has_permission(request, view)
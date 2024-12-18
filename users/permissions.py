from rest_framework.permissions import BasePermission


class IsActive(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_active


class IsSuperuser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser


class IsActiveAndNotSuperuser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_active and not request.user.is_superuser

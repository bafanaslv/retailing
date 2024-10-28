from rest_framework.permissions import BasePermission


class IsActive(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.is_active


class IsSuperuser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.is_superuser


class IsActiveAndNotIsSuperuser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(obj.is_active and not obj.is_superuser)

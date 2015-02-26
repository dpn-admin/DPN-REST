"""
    Knowledge is knowing a tomato is a fruit; wisdom is not putting it in a
    fruit salad.
                - Miles Kington
"""

from rest_framework import permissions

from dpn.data.models import UserProfile

class IsNodeUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Any authenticated user can read, but to write permissions
        # are stricter.
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_superuser:
            return True
        else:
            if (request.user.profile.node == obj.from_node or
                request.user.profile.node == obj.to_node):
                return True
        return False

class IsBagOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_superuser:
            # Should we allow superuser to update any bags??
            return True
        else:
            return (request.user.profile.node == obj.admin_node
                    and obj.pk is not None)

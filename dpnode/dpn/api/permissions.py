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
        else:
            if request.user.is_superuser:
                return True
            if (request.user.profile.node == obj.from_node or
                request.user.profile.node == obj.to_node):
                return True
            return False

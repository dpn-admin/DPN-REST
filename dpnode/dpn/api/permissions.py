__author__ = 'swt8w'

from rest_framework import permissions

from dpn.data.models import UserProfile

class IsNodeUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        profile = UserProfile.objects.get(user=self.request.user)
        if profile.node == obj.node:
            return True
        return False
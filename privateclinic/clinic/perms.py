from rest_framework import permissions


class AccountOwnerAuthenticated(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view) and request.user == obj

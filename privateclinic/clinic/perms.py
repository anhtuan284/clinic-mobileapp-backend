from rest_framework import permissions
from oauth2_provider.models import AccessToken
from rest_framework.permissions import BasePermission
from django.utils import timezone


class AccountOwnerAuthenticated(permissions.IsAuthenticated):
    message = 'Not your Account'

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view) and request.user == obj


class IsInGroup(BasePermission):
    message = 'You do not have permission to perform this action'

    def __init__(self, allowed_groups):
        self.allowed_groups = allowed_groups

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        user_groups = request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in self.allowed_groups)


def check_token_expiration(token):
    access_token = AccessToken.objects.get(token=token)
    expiration_time = access_token.expires

    if expiration_time < timezone.now():
        print("Access token has expired.")
    else:
        print("Access token is still valid.")


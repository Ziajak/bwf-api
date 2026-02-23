from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils import timezone
from .models import Member


class IsSuperUserOnly(BasePermission):
    message = "Only global user allowed"

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )

class GroupPermission(BasePermission):
    message = "You are not allowed to perform this action"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method == 'POST':
            return request.user.is_superuser

        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = request.user

        is_admin = Member.objects.filter(
            user=user,
            group=obj,
            admin=True
        ).exists()

        if user.is_superuser or is_admin:
            return True

        self.message = "Only superuser or group admin allowed"
        return



class UserPermission(BasePermission):
    message = "You are not allowed to access users"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # admin jakiejkolwiek grupy → GET only
        if request.method in SAFE_METHODS:
            return Member.objects.filter(
                user=request.user,
                admin=True
            ).exists()

        return False

class SetAdminPermission(BasePermission):
    message = "You must be group admin"

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        user_id = request.data.get('user_id')
        group_id = request.data.get('group_id')


        if not user_id or not group_id:
            return False

        from .models import User, Member
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return False


        if target_user.is_superuser:
            self.message = 'You can not revoke group admin privileges for a superuser'
            return False

        is_admin_in_group = Member.objects.filter(
            user=user,
            group_id=group_id,
            admin=True
        ).exists()

        return is_admin_in_group

class IsGroupAdminForEventCreate(BasePermission):
    message = "You have to be global admin"

    def has_permission(self, request, view):
        if request.method not in ('POST', 'UPDATE', 'DELETE'):
            return True

        group_id = request.data.get('group')

        if not group_id or not request.user.is_authenticated:
            return False

        if request.user.is_authenticated and request.user.is_superuser:
            return True

        is_admin = Member.objects.filter(
            user = request.user,
            group = group_id,
            admin = True
        ).exists()

        if not is_admin:
            self.message = 'You have to be group admin'
            return False

        return True

    def has_object_permission(self, request, view, obj):
        if request.method not in ["PUT", "UPDATE", "DELETE"]:
            return True

        if obj.time >= timezone.now():
            self.message = 'The event does not finish!'
            return False

        is_admin = Member.objects.filter(
            user=request.user,
            group=obj.group,
            admin=True
        ).exists()

        if request.user.is_superuser:
            return True

        if not is_admin:
            self.message = "You have to be group admin"
            return False

        return True
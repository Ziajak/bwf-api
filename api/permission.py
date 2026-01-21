from rest_framework.permissions import BasePermission
from django.utils import timezone
from .models import Member

class IsGroupAdminForEventCreate(BasePermission):
    message = "You have to be admin of group to create, update or delete the event!"

    def has_permission(self, request, view):
        if request.method not in ('POST', 'UPDATE', 'DELETE'):
            return True

        group_id = request.data.get('group')

        if not group_id or not request.user.is_authenticated:
            return False

        return Member.objects.filter(
            user = request.user,
            group = group_id,
            admin = True
        ).exists()

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
        if not is_admin:
            self.message = "You have to be admin of the group to modify this event!"
            return False

        return True
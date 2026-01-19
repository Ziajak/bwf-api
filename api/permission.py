from rest_framework.permissions import BasePermission
from django.utils import timezone
from .models import Member

class IsGroupAdminAndEventFinished(BasePermission):
    message = "You must be a group admin and the event must be finished."

    def has_object_permission(self, request, view, obj):
        if request.method not in ["PUT", "PATCH"]:
            return True

        if obj.time >= timezone.now():
            return False

        return Member.objects.filter(
            user=request.user,
            group=obj.group,
            admin=True
        ).exists()

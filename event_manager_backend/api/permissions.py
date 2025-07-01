from rest_framework import permissions
from .models import EventAttendee

class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Allow organizers of the event, or superusers, to edit/delete; others: read-only.
    """

    # PUBLIC_INTERFACE
    def has_object_permission(self, request, view, obj):
        """Grant full access to organizers or superusers, else only read."""
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        return EventAttendee.objects.filter(user=request.user, event=obj, role="organizer").exists()

class IsSelfOrAdmin(permissions.BasePermission):
    """
    Users can only edit their own details, except superusers/staff.
    """
    # PUBLIC_INTERFACE
    def has_object_permission(self, request, view, obj):
        """Grant access if user is self or admin."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        return obj == request.user

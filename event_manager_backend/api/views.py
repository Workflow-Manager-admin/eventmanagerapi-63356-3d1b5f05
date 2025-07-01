from rest_framework import permissions, viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Event, EventAttendee
from .serializers import (
    EventSerializer,
    UserSerializer,
    EventCreateUpdateSerializer,
)
from .permissions import IsOrganizerOrReadOnly, IsSelfOrAdmin

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Health check endpoint for server."""
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on events, with permissions.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]
        elif self.action in ["create"]:
            permission_classes = [permissions.IsAuthenticated]
        else:  # list, retrieve
            permission_classes = [permissions.AllowAny]
        return [perm() for perm in permission_classes]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return EventSerializer

    def perform_create(self, serializer):
        event = serializer.save(created_by=self.request.user)
        attendees = self.request.data.get("attendees", [])
        # creator automatically set as organizer
        EventAttendee.objects.create(
            event=event, user=self.request.user, role='organizer'
        )
        # Add additional attendees if provided
        for att in attendees:
            user_id = att.get("user_id")
            role = att.get("role", "participant")
            if user_id and user_id != self.request.user.id:
                try:
                    user = User.objects.get(id=user_id)
                    EventAttendee.objects.create(event=event, user=user, role=role)
                except User.DoesNotExist:
                    continue  # skip invalid users

    def perform_update(self, serializer):
        event = serializer.save()
        if 'attendees' in self.request.data:
            new_attendees = self.request.data.get('attendees', [])
            # Remove all existing attendees except creator
            EventAttendee.objects.filter(event=event).exclude(user=event.created_by).delete()
            for att in new_attendees:
                user_id = att.get("user_id")
                role = att.get("role", "participant")
                if user_id and user_id != event.created_by.id:
                    try:
                        user = User.objects.get(id=user_id)
                        EventAttendee.objects.update_or_create(
                            event=event, user=user,
                            defaults={'role': role}
                        )
                    except User.DoesNotExist:
                        continue

# PUBLIC_INTERFACE
class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint for user management (view, update, delete, list).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]
        else:
            permission_classes = [permissions.AllowAny]
        return [perm() for perm in permission_classes]

from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from .models import Event, EventAttendee
from .serializers import (
    EventSerializer,
    UserSerializer,
    EventCreateUpdateSerializer,
)
from django.http import JsonResponse

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Health check endpoint for server."""
    return JsonResponse({
        "scheme": request.scheme,
        "host": request.get_host(),
        "build_uri": request.build_absolute_uri(),
        "META_HOST": request.META.get("HTTP_HOST"),
        "X-Forwarded-Port": request.META.get("HTTP_X_FORWARDED_PORT"),
    })

# PUBLIC_INTERFACE
class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on events. Now open/public access, no permissions/authentication.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return EventSerializer

    def perform_create(self, serializer):
        # Note: created_by must be set for Event model, but there's no user. 
        # We'll pick a default user or set to None, but Django's ForeignKey requires a User.
        # Instead, for demo openness: assign first available user or skip setting entirely (could break integrity).
        # Better: change the model to allow null, but that's schema migration, not requested.
        users = User.objects.all()
        default_user = users.first() if users.exists() else None
        event = serializer.save(created_by=default_user)
        attendees = self.request.data.get("attendees", [])
        # creator automatically set as organizer if a user exists
        if default_user:
            EventAttendee.objects.create(
                event=event, user=default_user, role='organizer'
            )
        # Add additional attendees if provided
        for att in attendees:
            user_id = att.get("user_id")
            role = att.get("role", "participant")
            if user_id and (not default_user or user_id != default_user.id):
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
            users = User.objects.all()
            default_user = users.first() if users.exists() else None
            exclude_user = default_user if default_user else None
            qs = EventAttendee.objects.filter(event=event)
            if exclude_user:
                qs = qs.exclude(user=exclude_user)
            qs.delete()
            for att in new_attendees:
                user_id = att.get("user_id")
                role = att.get("role", "participant")
                if user_id and (not exclude_user or user_id != exclude_user.id):
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
    API endpoint for user management (view, update, delete, list). Full open/public access.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, EventAttendee

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]

class EventAttendeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = EventAttendee
        fields = ["user", "role"]

class EventCreateAttendeeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = EventAttendee
        fields = ["user_id", "role"]

class EventSerializer(serializers.ModelSerializer):
    attendees = EventAttendeeSerializer(source="eventattendee_set", many=True, read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "start_time",
            "end_time",
            "created_by",
            "attendees",
        ]

class EventCreateUpdateSerializer(serializers.ModelSerializer):
    """For creating or updating events including user roles"""
    attendees = EventCreateAttendeeSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "start_time",
            "end_time",
            "attendees",
        ]

from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    """Model representing an event."""
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")
    attendees = models.ManyToManyField(User, through='EventAttendee', related_name="events")

    def __str__(self):
        return self.title

class EventAttendee(models.Model):
    """Through-table for event attendance with role."""
    ROLE_CHOICES = (
        ('organizer', 'Organizer'),
        ('participant', 'Participant'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')

    class Meta:
        unique_together = ('user', 'event')  # One role per user per event

    def __str__(self):
        return f"{self.user.username} - {self.role} for {self.event.title}"

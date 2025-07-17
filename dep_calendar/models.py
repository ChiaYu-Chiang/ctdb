from django.db import models
from django.contrib.auth.models import User, Group

class CalendarEvent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    department = models.ForeignKey(Group, on_delete=models.CASCADE, limit_choices_to={'groupprofile__is_department': True})
    participants = models.ManyToManyField(User, related_name='calendar_events', blank=True)

    def __str__(self):
        return self.title

    def can_user_access(self, user):
        # 限同部門可見
        if not hasattr(user, 'profile'):
            return False
        return user.profile.activated_role == self.department
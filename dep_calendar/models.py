from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _

class CalendarEvent(models.Model):
    EVENT_TYPE = [
        (_('field_work'), (
            ('installation', _('installation')),
            ('maintenance', _('maintenance')),
            ('termination', _('termination')),
        )
        ),
        (_('other_field'), (
            ('facility_inspection', _('facility_inspection')),
            ('local_support', _('local_support')),
            ('others', _('others')),
        )
        ),
    ]
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    event_type = models.CharField(verbose_name=_('Event type'), max_length=63, choices=EVENT_TYPE)
    description = models.TextField(blank=True, verbose_name=_('Description'))
    start_time = models.DateTimeField(verbose_name=_('Start time'))
    end_time = models.DateTimeField(verbose_name=_('End time'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', verbose_name=_('Created by'))
    department = models.ForeignKey(Group, on_delete=models.CASCADE, limit_choices_to={'groupprofile__is_department': True}, verbose_name=_('Department'))
    participants = models.ManyToManyField(User, related_name='calendar_events', blank=True, verbose_name=_('Participants'))

    def __str__(self):
        return self.title

    def can_user_access(self, user):
        if not hasattr(user, 'profile'):
            return False
        return user.profile.activated_role == self.department
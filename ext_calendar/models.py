from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _

class SupportGroup(models.Model):
    name = models.CharField(max_length=10, unique=True)
    def __str__(self):
        return self.name

class CalendarEvent(models.Model):
    SUPPORT_CONSULTANT = [
        (_('S11'), (
            ('Ken', 'Ken'),
            ('Esther', 'Esther'),
            ('Stephanie', 'Stephanie'),
            ('Ariel', 'Ariel'),
        )),
        (_('S12'), (
            ('Vivi', 'Vivi'),
            ('Amanda', 'Amanda'),
            ('Vicky', 'Vicky'),
            ('Cora', 'Cora'),
            ('Danny', 'Danny'),
        )),
        (_('S21'), (
            ('Claire', 'Claire'),
            ('Geoff', 'Geoff'),
            ('Novia', 'Novia'),
            ('Lear', 'Lear'),
            ('Bryan', 'Bryan'),
            ('Tina', 'Tina'),
            ('James', 'James'),
            ('Judy', 'Judy'),
            ('Fly', 'Fly'),
        )),
        (_('S23'), (
            ('Vita', 'Vita'),
            ('David', 'David'),
            ('Allen', 'Allen'),
            ('Karen', 'Karen'),
            ('Leo', 'Leo'),
            ('William', 'William'),
            ('May', 'May'),
            ('Vivian', 'Vivian'),
        )),
        (_('D11'), (
            ('Ginny', 'Ginny'),
            ('Karen', 'Karen'),
            ('Tony', 'Tony'),
            ('Charline', 'Charline'),
            ('Jeff', 'Jeff'),
            ('Jack', 'Jack'),
            ('Stallone', 'Stallone'),
        )),
    ]

    PRODUCT_TYPE = [
        ('IDC', 'IDC'),
        ('MPLS', 'MPLS'),
        ('MPLS-SDWAN', 'MPLS-SDWAN'),
        ('IPLC', 'IPLC'),
        ('TPIX', 'TPIX'),
        ('IPT', 'IPT'),
        ('CIX', 'CIX'),
        ('CCX', 'CCX'),
        ('Chief Cloud', 'Chief Cloud'),
        ('轉售/代收代付', '轉售/代收代付'),
    ]

    title = models.CharField(max_length=255, verbose_name=_('Title'))
    support_group = models.ManyToManyField(SupportGroup, verbose_name=_('Support Group'), blank=True)
    support_consultant = models.CharField(verbose_name=_('Support Consultant'), max_length=500, blank=True, choices=SUPPORT_CONSULTANT)
    client_name = models.CharField(max_length=255, verbose_name=_('Client Name'))
    product_type = models.CharField(verbose_name=_('Product Type'), max_length=20, choices=PRODUCT_TYPE)
    description = models.TextField(blank=True, verbose_name=_('Description'))
    start_time = models.DateTimeField(verbose_name=_('Start time'))
    end_time = models.DateTimeField(verbose_name=_('End time'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ext_created_events', verbose_name=_('Created by'))
    department = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='ext_department_events', limit_choices_to={'groupprofile__is_department': True}, verbose_name=_('Department'))
    participants = models.ManyToManyField(User, related_name='ext_calendar_events', blank=True, verbose_name=_('Participants'))

    def __str__(self):
        return self.title

    def can_user_access(self, user):
        if not hasattr(user, 'profile'):
            return False
        return user.profile.activated_role == self.department
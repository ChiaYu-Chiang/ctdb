from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.utils import today


class Diary(models.Model):
    date = models.DateField(verbose_name=_('Date'), default=today)
    daily_check = models.CharField(
        verbose_name=_('Daily check'),
        max_length=15,
        choices=(
            ('yes', _('Yes')),
            ('no', _('No')),
        ),
        default='no',
    )
    daily_record = models.TextField(verbose_name=_('Daily record'))
    todo = models.TextField(verbose_name=_('To do'), blank=True)
    remark = models.TextField(verbose_name=_('Remark'), blank=True)
    comment = models.TextField(verbose_name=_('Comment'), blank=True)
    created_by = models.ForeignKey(verbose_name=_('Created by'), to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date']
        verbose_name = _('Diary')
        verbose_name_plural = _('Diaries')
        unique_together = (('date', 'created_by'), )

    def __str__(self):
        return self.daily_record[:8] + '..'

    def get_create_url(self):
        return reverse('diary:diary_create')

    def get_update_url(self):
        return reverse('diary:diary_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('diary:diary_delete', kwargs={'pk': self.pk})

    def get_clone_url(self):
        return reverse('diary:diary_clone', kwargs={'pk': self.pk})

    def get_comment_url(self):
        return reverse('diary:diary_comment', kwargs={'pk': self.pk})

    def get_work_hours_display(self):
        """
        Human readable summary of related `DiaryWorkHour` entries, one item
        per line (rendered via the `linebreaksbr` filter in diary_list.html):
        "<order_number> <customer_name>：<hours>hr". Only meaningful for I02
        diaries; used when `show_work_hours` is True.
        """
        lines = []
        for work_hour in self.work_hours.all():
            label = ' '.join(filter(None, [work_hour.order_number, work_hour.customer_name]))
            lines.append(f'{label}：{work_hour.hours}hr')
        return '\n'.join(lines)

    def get_work_hours_total(self):
        return self.work_hours.aggregate(total=Sum('hours'))['total'] or 0


class DiaryWorkHour(models.Model):
    """
    A single row of I02's "作業處理時數統計" (work-hours processing log)
    belonging to a `Diary`. Only created/shown for I02 diaries (see
    `diary.views.is_i02_role`) — other departments' diaries simply have no
    related rows here.
    """
    diary = models.ForeignKey(Diary, verbose_name=_('Diary'), related_name='work_hours', on_delete=models.CASCADE)
    order_number = models.CharField(verbose_name=_('Order number'), max_length=100, blank=True)
    customer_name = models.CharField(verbose_name=_('Customer name'), max_length=100, blank=True)
    sales_rep = models.CharField(verbose_name=_('Sales rep'), max_length=100, blank=True)
    product_category = models.CharField(verbose_name=_('Product category'), max_length=100, blank=True)
    requirement = models.CharField(verbose_name=_('Requirement'), max_length=255, blank=True)
    handling_content = models.TextField(verbose_name=_('Handling content'), blank=True)
    hours = models.DecimalField(verbose_name=_('Hours'), max_digits=5, decimal_places=1)
    order = models.PositiveIntegerField(verbose_name=_('Order'), default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('Diary work hour')
        verbose_name_plural = _('Diary work hours')

    def __str__(self):
        return f'{self.customer_name or self.order_number or self.id}：{self.hours}'
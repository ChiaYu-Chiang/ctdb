from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.utils import now


class News(models.Model):

    title = models.TextField(verbose_name=_('Title'))
    content = models.TextField(verbose_name=_('Content'))
    is_pinned = models.BooleanField(verbose_name=_('Is pinned'), default=False)
    at = models.DateTimeField(verbose_name=_('at'), default=now)
    due = models.DateTimeField(verbose_name=_('Due'), null=True, blank=True)
    created_by = models.ForeignKey(verbose_name=_('Created by'), to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-is_pinned', '-at']
        verbose_name = _('New')
        verbose_name_plural = _('News')

    def get_create_url(self):
        return reverse('news:news_create')

    def get_update_url(self):
        return reverse('news:news_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('news:news_delete', kwargs={'pk': self.pk})


class NewsReadRecord(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='read_records', verbose_name=_('News'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'))
    read_at = models.DateTimeField(verbose_name=_('Read at'), auto_now_add=True)

    class Meta:
        unique_together = ('news', 'user')
        verbose_name = _('News Read Record')
        verbose_name_plural = _('News Read Records')

    def __str__(self):
        return f"{self.user.username} already read news: {self.news.title}"

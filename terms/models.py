from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class Terms(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    short_name = models.CharField(max_length=100, verbose_name=_('Short Name'))
    full_name = models.CharField(max_length=255, verbose_name=_('Full Name'))
    url = models.URLField(max_length=255, blank=True, null=True, verbose_name=_('URL'))
    management_department = models.CharField(max_length=255, verbose_name=_('Management Department'))
    description = models.TextField(verbose_name=_('Description'))
    created_by = models.ForeignKey(verbose_name=_('Created by'), to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name = _('Terms')
        verbose_name_plural = _('Terms')
    def __str__(self):
        return f'{self.short_name} - {self.full_name}'
    
    def get_absolute_url(self):
        return reverse('terms:terms_detail', kwargs={'pk': self.pk})

    def get_create_url(self):
        return reverse('terms:terms_create')

    def get_update_url(self):
        return reverse('terms:terms_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('terms:terms_delete', kwargs={'pk': self.pk})

    @property
    def has_external_link(self):
        return bool(self.url)
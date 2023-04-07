from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class Tool(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    created_by = models.ForeignKey(verbose_name=_('Created by'), to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name = _('Tool')
        verbose_name_plural = _('Tools')

    def __str__(self):
        return f'{self.name}'

    def get_create_url(self):
        return reverse('tool:tool_create')

    def get_update_url(self):
        return reverse('tool:tool_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('tool:tool_delete', kwargs={'pk': self.pk})
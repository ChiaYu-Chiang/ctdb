from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import os

from .storage import UUIDFileSystemStorage

uuid_file_system_storage = UUIDFileSystemStorage()


class Archive(models.Model):
    archive = models.FileField(storage=uuid_file_system_storage, upload_to='archive')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']
        verbose_name = _('Archive')
        verbose_name_plural = _('Archives')

    def __str__(self):
        return self.name

    def get_create_url(self):
        return reverse('archive:archive_create')

    def get_update_url(self):
        return reverse('archive:archive_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('archive:archive_delete', kwargs={'pk': self.pk})

    def get_create_journals_url(self):
        return reverse('archive:journals_create')

    def get_create_announce_url(self):
        return reverse('archive:announce_create')

    def get_full_filename(self):
        _, extension = os.path.splitext(self.archive.name)
        return f"{self.name}{extension}"

    def get_convert_to_reminders_url(self):
        """取得轉換為提醒的 URL"""
        return reverse('archive:convert_to_reminders', kwargs={'pk': self.pk})

    def is_excel_file(self):
        """檢查是否為 Excel 檔案"""
        if self.archive and self.archive.name:
            return self.archive.name.lower().endswith(('.xlsx', '.xls'))
        return False
    
    def can_convert_to_reminders(self):
        """檢查是否可以轉換為提醒（必須是包含網應處月會行事曆的 Excel 檔案）"""
        return (self.is_excel_file() and 
                self.name and 
                '網應處月會行事曆' in self.name)

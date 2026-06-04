from django.contrib import admin

from .models import Archive

class ArchiveAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['type', 'is_permanent', 'visible_at', 'visible_due', 'created_by']
    list_display = ['name', 'type', 'is_permanent', 'visible_at', 'visible_due', 'created_by']
    list_editable = ['is_permanent', 'visible_at', 'visible_due']

admin.site.register(Archive, ArchiveAdmin)
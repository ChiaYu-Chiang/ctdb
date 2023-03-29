from django.contrib import admin

from .models import Tool


class ToolAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'name', 'url']
    list_editable = ['name', 'url']


admin.site.register(Tool, ToolAdmin)
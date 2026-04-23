from django.contrib import admin

from .models import CalendarEvent, SupportGroup

admin.site.register(CalendarEvent)
admin.site.register(SupportGroup)

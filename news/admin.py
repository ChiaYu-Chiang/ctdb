from django.contrib import admin

from .models import News

class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'content', 'is_pinned', 'at', 'due', 'created_by']
    list_editable = ['is_pinned', 'at', 'due']

admin.site.register(News, NewsAdmin)

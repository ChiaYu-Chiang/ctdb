from django.contrib import admin

from .models import News, NewsReadRecord

class NewsAdmin(admin.ModelAdmin):
    search_fields = ['title', 'content']
    list_filter = ['is_pinned', 'is_permanent', 'at', 'due', 'visible_at', 'visible_due', 'created_by']
    list_display = ['title', 'content', 'is_pinned', 'is_permanent', 'at', 'due', 'visible_at', 'visible_due', 'created_by']
    list_editable = ['is_pinned', 'is_permanent', 'at', 'due', 'visible_at', 'visible_due']

admin.site.register(News, NewsAdmin)

@admin.register(NewsReadRecord)
class NewsReadRecordAdmin(admin.ModelAdmin):
    list_display = ('news', 'user', 'read_at')
    list_filter = ('news', 'user')
    search_fields = ('news__title', 'user__username')
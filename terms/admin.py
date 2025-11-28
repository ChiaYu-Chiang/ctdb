from django.contrib import admin
from .models import Terms

@admin.register(Terms)
class TermsAdmin(admin.ModelAdmin):
    list_display = ['id', 'short_name', 'full_name', 'management_department', 'created_by']
    list_editable = ['short_name', 'full_name', 'management_department']
    list_filter = ['management_department', 'created_by']
    search_fields = ['short_name', 'full_name', 'description']
    readonly_fields = ['created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # 如果是新建
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
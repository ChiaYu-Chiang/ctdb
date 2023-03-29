from django.urls import path

from .views import tool_list, tool_create, tool_delete, tool_update

app_name = 'tool'

urlpatterns = [
    path('tools/', tool_list, name='tool_list'),
    path('tools/add/', tool_create, name='tool_create'),
    path('tools/<int:pk>/change/', tool_update, name='tool_update'),
    path('tools/<int:pk>/delete/', tool_delete, name='tool_delete'),
]
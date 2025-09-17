from django.urls import path

from .views import (
    archive_create,
    archive_delete,
    archive_list,
    archive_update,
    journals_list,
    journals_create,
    announce_list,
    announce_create,
    convert_to_reminders,
)

app_name = 'archive'

urlpatterns = [
    path('archives/', archive_list, name='archive_list'),
    path('archives/add/', archive_create, name='archive_create'),
    path('archives/<int:pk>/change/', archive_update, name='archive_update'),
    path('archives/<int:pk>/delete/', archive_delete, name='archive_delete'),
    path('archives/journals/', journals_list, name='journals_list'),
    path('archives/journals/add/', journals_create, name='journals_create'),
    path('archives/announce/', announce_list, name='announce_list'),
    path('archives/announce/add/', announce_create, name='announce_create'),
    path('archives/<int:pk>/convert-to-reminders/', convert_to_reminders, name='convert_to_reminders'),
]

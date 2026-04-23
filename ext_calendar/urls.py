from django.urls import path
from . import views

app_name = 'ext_calendar'

urlpatterns = [
    path('ext_calendar/', views.event_list, name='event_list'),
    path('ext_calendar/events/json/', views.calendar_events_json, name='calendar_events_json'),
    path('ext_calendar/event/create/', views.event_create, name='event_create'),
    path('ext_calendar/event/<int:pk>/', views.event_detail, name='event_detail'),
    path('ext_calendar/event/<int:pk>/change/', views.event_update, name='event_update'),
    path('ext_calendar/event/<int:pk>/delete/', views.event_delete, name='event_delete'),
]
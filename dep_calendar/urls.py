from django.urls import path
from . import views

app_name = 'dep_calendar'

urlpatterns = [
    path('dep_calendar/', views.event_list, name='event_list'),
    path('dep_calendar/events/json/', views.calendar_events_json, name='calendar_events_json'),
    path('dep_calendar/event/create/', views.event_create, name='event_create'),
    path('dep_calendar/event/<int:pk>/', views.event_detail, name='event_detail'),
    path('dep_calendar/event/<int:pk>/change/', views.event_update, name='event_update'),
    path('dep_calendar/event/<int:pk>/delete/', views.event_delete, name='event_delete'),
]
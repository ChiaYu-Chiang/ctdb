from django.urls import path
from .views import (event_list, event_create, calendar_events_json)

app_name = 'dep_calendar'

urlpatterns = [
    path('dep_calendar/', event_list, name='event_list'),
    path('dep_calnedar/events/', calendar_events_json, name='calendar_events_json'),
    path('dep_calnedar/add/', event_create, name='event_create'),
]
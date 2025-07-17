from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import CalendarEvent
from .forms import CalendarEventForm

@login_required
def event_list(request):
    return render(request, 'dep_calendar/calendar.html')

@login_required
def calendar_events_json(request):
    user_department = request.user.profile.activated_role
    events = CalendarEvent.objects.filter(department=user_department)

    data = [{
        'id': e.id,
        'title': e.title,
        'start': e.start_time.isoformat(),
        'end': e.end_time.isoformat(),
    } for e in events]

    return JsonResponse(data, safe=False)

@login_required
def event_create(request):
    user_department = request.user.profile.activated_role
    form_buttons = ['create']
    if request.method == 'POST':
        form = CalendarEventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.department = user_department
            event.save()
            form.save_m2m()
            return redirect('dep_calendar:event_list')
    else:
        form = CalendarEventForm(user=request.user)
    return render(request, 'dep_calendar/event_form.html', {'form': form, 'form_buttons': form_buttons})


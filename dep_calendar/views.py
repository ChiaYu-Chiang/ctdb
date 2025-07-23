from django.contrib.auth.decorators import login_required
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import JsonResponse
from django.utils.translation import gettext as _

from core.decorators import permission_required

from .forms import CalendarEventForm
from .models import CalendarEvent

def get_event_queryset(request):
    model = CalendarEvent
    user_department = request.user.profile.activated_role
    queryset = model.objects.all()
    if not user_department:
        return queryset.fileter(created_by=request.user)
    return queryset.filter(department=user_department)

@login_required
@permission_required('dep_calendar.view_calendarevent', raise_exception=True, exception=Http404)
def event_list(request):
    template_name = 'dep_calendar/calendar.html'
    return render(request, template_name)

@login_required
def calendar_events_json(request):
    user_department = request.user.profile.activated_role
    events = CalendarEvent.objects.filter(department=user_department)

    color_palette = ['#1abc9c', '#3498db', '#f39c12', '#9b59b6', '#e74c3c']

    data = []
    for e in events:
        color_index = e.created_by.id % len(color_palette)
        data.append({
            'id': e.id,
            'title': e.title,
            'start': e.start_time.isoformat(),
            'end': e.end_time.isoformat(),
            'color': color_palette[color_index],
        })

    return JsonResponse(data, safe=False)

@login_required
@permission_required('dep_calendar.add_calendarevent', raise_exception=True, exception=Http404)
def event_create(request):
    model = CalendarEvent
    instance = model(created_by=request.user)
    form_class = CalendarEventForm
    success_url = reverse('dep_calendar:event_list')
    form_buttons = ['create']
    template_name = 'dep_calendar/event_form.html'
    user_department = request.user.profile.activated_role
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.department = user_department
            event.save()
            form.save_m2m()
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class(user=request.user)
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)

@login_required
@permission_required('dep_calendar.change_calendarevent', raise_exception=True, exception=Http404)
def event_update(request, pk):
    model = CalendarEvent
    queryset = get_event_queryset(request)
    event = get_object_or_404(CalendarEvent, pk=pk, created_by=request.user)
    form_class = CalendarEventForm
    success_url = reverse('dep_calendar:event_list')
    form_buttons = ['update']
    template_name = 'dep_calendar/event_form.html'
    if request.method == 'POST':
        form = form_class(request.POST, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class(instance=event, user=request.user)
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)

@login_required
@permission_required('dep_calendar.delete_calendarevent', raise_exception=True, exception=Http404)
def event_delete(request, pk):
    model = CalendarEvent
    event = get_object_or_404(model, pk=pk, created_by=request.user)
    success_url = reverse('dep_calendar:event_list')
    template_name = 'dep_calendar/event_confirm_delete.html'
    if request.method == 'POST':
        event.delete()
        return redirect(success_url)
    context = {'model': model}
    return render(request, template_name, context)

@login_required
@permission_required('dep_calendar.view_calendarevent', raise_exception=True, exception=Http404)
def event_detail(request, pk):
    queryset = get_event_queryset(request)
    event = get_object_or_404(CalendarEvent, pk=pk)
    template_name = 'dep_calendar/event_detail.html'
    context = {'event': event}
    return render(request, template_name, context)
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
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
            messages.success(request, _('事件已成功新增！'))
            return redirect('dep_calendar:event_list')
    else:
        form = CalendarEventForm(user=request.user)
    return render(request, 'dep_calendar/event_form.html', {'form': form, 'form_buttons': form_buttons})

@login_required
def event_update(request, pk):
    event = get_object_or_404(CalendarEvent, id=pk)
    user_department = request.user.profile.activated_role
    
    # 檢查權限 - 只有同部門的人才能編輯
    if not event.can_user_access(request.user):
        return HttpResponseForbidden("您沒有權限編輯此事件")
    
    form_buttons = ['update']
    if request.method == 'POST':
        form = CalendarEventForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('事件已成功更新！'))
            return redirect('dep_calendar:event_list')
    else:
        form = CalendarEventForm(instance=event, user=request.user)
    
    return render(request, 'dep_calendar/event_form.html', {
        'form': form, 
        'form_buttons': form_buttons,
        'event': event
    })

@login_required
def event_delete(request, pk):
    event = get_object_or_404(CalendarEvent, id=pk)
    
    # 檢查權限 - 只有同部門的人才能刪除
    if not event.can_user_access(request.user):
        return HttpResponseForbidden("您沒有權限刪除此事件")
    
    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(request, _('事件「{}」已成功刪除！').format(event_title))
        return redirect('dep_calendar:event_list')
    
    return render(request, 'dep_calendar/event_confirm_delete.html', {'event': event})

@login_required
def event_detail(request, pk):
    event = get_object_or_404(CalendarEvent, id=pk)
    
    # 檢查權限 - 只有同部門的人才能查看
    if not event.can_user_access(request.user):
        return HttpResponseForbidden("您沒有權限查看此事件")
    
    return render(request, 'dep_calendar/event_detail.html', {'event': event})
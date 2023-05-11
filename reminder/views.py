from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import urllib.parse

from core.decorators import permission_required
from core.utils import remove_unnecessary_seperator

from .forms import ReminderModelForm
from .models import Reminder


def get_reminder_queryset(request):
    """
    The queryset of model `Reminder` with filter depending on user's role/identity/group.
    The views below will use this as a basic queryset. This ensures that users won't
    accidentally see or touch those they shouldn't.
    """
    model = Reminder
    queryset = model.objects.all()
    role = request.user.profile.activated_role
    deps = request.user.groups.filter(groupprofile__is_department=True)
    if not role:
        return queryset.filter(created_by__groups__in=deps).distinct()
    supervise_roles = role.groupprofile.supervise_roles.all()
    if not supervise_roles:
        return queryset.filter(created_by__groups__in=deps).distinct()
    return queryset.filter(created_by__groups__in=supervise_roles).distinct()


@login_required
@permission_required('reminder.view_reminder', raise_exception=True, exception=Http404)
def reminder_list(request):
    model = Reminder
    queryset = get_reminder_queryset(request)
    paginate_by = 5
    template_name = 'reminder/reminder_list.html'
    create_by = request.GET.get('created_by')
    queryset = queryset.filter(created_by=request.user) if create_by else queryset
    page_number = request.GET.get('page', '')
    paginator = Paginator(queryset, paginate_by)
    page_obj = paginator.get_page(page_number)
    is_paginated = page_number.lower() != 'all' and page_obj.has_other_pages()
    context = {
        'model': model,
        'page_obj': page_obj,
        'object_list': page_obj if is_paginated else queryset,
        'is_paginated': is_paginated,
        'create_by': create_by,
    }
    return render(request, template_name, context)


@login_required
@permission_required('reminder.add_reminder', raise_exception=True, exception=Http404)
def reminder_create(request):
    model = Reminder
    instance = model(created_by=request.user)
    form_class = ReminderModelForm
    success_url = reverse('reminder:reminder_list')
    form_buttons = ['create']
    template_name = 'reminder/reminder_form.html'
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class()
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)


@login_required
@permission_required('reminder.change_reminder', raise_exception=True, exception=Http404)
def reminder_update(request, pk):
    model = Reminder
    queryset = get_reminder_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk, created_by=request.user)
    form_class = ReminderModelForm
    success_url = reverse('reminder:reminder_list')
    form_buttons = ['update']
    template_name = 'reminder/reminder_form.html'
    create_by = request.GET.get('created_by')
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            if create_by:
                success_url += f'?created_by={create_by}'
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class(instance=instance)
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)


@login_required
@permission_required('reminder.delete_reminder', raise_exception=True, exception=Http404)
def reminder_delete(request, pk):
    model = Reminder
    queryset = get_reminder_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk, created_by=request.user)
    success_url = reverse('reminder:reminder_list')
    template_name = 'reminder/reminder_confirm_delete.html'
    create_by = request.GET.get('created_by')
    if request.method == 'POST':
        instance.delete()
        if create_by:
            success_url += f'?created_by={create_by}'
        return redirect(success_url)
    context = {'model': model}
    return render(request, template_name, context)


@login_required
@permission_required('reminder.change_reminder', raise_exception=True, exception=Http404)
def reminder_clone(request, pk):
    model = Reminder
    queryset = get_reminder_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk, created_by=request.user)
    instance.pk = None
    form_class = ReminderModelForm
    success_url = reverse('reminder:reminder_list')
    form_buttons = ['create']
    template_name = 'reminder/reminder_form.html'
    create_by = request.GET.get('created_by')
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            if create_by:
                success_url += f'?created_by={create_by}'
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class(instance=instance)
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)


@login_required
@permission_required('reminder.change_reminder', raise_exception=True, exception=Http404)
def reminder_send_email(request, pk):
    model = Reminder
    queryset = get_reminder_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk, created_by=request.user)
    success_url = reverse('reminder:reminder_list')
    template_name = 'reminder/reminder_confirm_send_email.html'
    create_by = request.GET.get('created_by')
    if request.method == 'POST':
        s = remove_unnecessary_seperator(instance.recipients, ';')
        recipient_list = list(map(str.strip, s.split(';')))
        send_mail(
            subject=instance.email_subject,
            message=instance.email_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        if create_by:
            success_url += f'?created_by={create_by}'
        return redirect(success_url)
    context = {'model': model}
    return render(request, template_name, context)

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings
from core.decorators import permission_required

from .forms import (IspGroupModelForm, IspModelForm,
                    PrefixListUpdateTaskModelForm)
from .models import Isp, IspGroup, PrefixListUpdateTask
from .sendtaskmail import handle_task_mail
from datetime import datetime
import os


def get_telecom_model_queryset(request, model):
    """
    The queryset of models `Isp`, `IspGroup`, `PrefixListUpdateTask` with
    filter depending on user's role/identity/group. The views below will use
    this as a basic queryset. This ensures that users won't accidentally see
    or touch those they shouldn't.
    """
    queryset = model.objects.all()
    role = request.user.profile.activated_role
    deps = request.user.groups.filter(groupprofile__is_department=True)
    if not role:
        return queryset.filter(created_by__groups__in=deps).distinct()
    supervise_roles = role.groupprofile.supervise_roles.all()
    if not supervise_roles:
        return queryset.filter(created_by__groups__in=deps).distinct()
    return queryset.filter(created_by__groups__in=supervise_roles).distinct()


def get_isp_queryset(request):
    model = Isp
    queryset = get_telecom_model_queryset(request, model=model)
    return queryset


def get_ispgroup_queryset(request):
    model = IspGroup
    queryset = get_telecom_model_queryset(request, model=model)
    return queryset


def get_prefixlistupdatetask_queryset(request):
    model = PrefixListUpdateTask
    queryset = get_telecom_model_queryset(request, model=model)
    return queryset


@login_required
@permission_required('telecom.view_isp', raise_exception=True, exception=Http404)
def isp_list(request):
    model = Isp
    queryset = get_isp_queryset(request)
    paginate_by = 5
    template_name = 'telecom/isp_list.html'
    page_number = request.GET.get('page', '')
    paginator = Paginator(queryset, paginate_by)
    page_obj = paginator.get_page(page_number)
    is_paginated = page_number.lower() != 'all' and page_obj.has_other_pages()
    context = {
        'model': model,
        'page_obj': page_obj,
        'object_list': page_obj if is_paginated else queryset,
        'is_paginated': is_paginated,
    }
    return render(request, template_name, context)


@login_required
@permission_required('telecom.add_isp', raise_exception=True, exception=Http404)
def isp_review(request, pk):
    model = Isp
    queryset = get_isp_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk)
    form_class = IspModelForm
    template_name = 'telecom/isp_form.html'
    form = form_class(instance=instance)
    for field in form.fields:
        form.fields[field].disabled = True
    context = {'model': model, 'form': form}
    return render(request, template_name, context)



@login_required
@permission_required('telecom.add_isp', raise_exception=True, exception=Http404)
def isp_create(request):
    model = Isp
    instance = model(created_by=request.user)
    form_class = IspModelForm
    success_url = reverse('telecom:isp_list')
    form_buttons = ['create']
    template_name = 'telecom/isp_form.html'
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
@permission_required('telecom.change_isp', raise_exception=True, exception=Http404)
def isp_update(request, pk):
    model = Isp
    queryset = get_isp_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk)
    form_class = IspModelForm
    success_url = reverse('telecom:isp_list')
    form_buttons = ['update']
    template_name = 'telecom/isp_form.html'
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class(instance=instance)
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)


@login_required
@permission_required('telecom.delete_isp', raise_exception=True, exception=Http404)
def isp_delete(request, pk):
    model = Isp
    queryset = get_isp_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk)
    success_url = reverse('telecom:isp_list')
    template_name = 'telecom/isp_confirm_delete.html'
    if request.method == 'POST':
        instance.delete()
        return redirect(success_url)
    context = {'model': model}
    return render(request, template_name, context)


@login_required
@permission_required('telecom.view_ispgroup', raise_exception=True, exception=Http404)
def ispgroup_list(request):
    model = IspGroup
    queryset = get_ispgroup_queryset(request)
    paginate_by = 5
    template_name = 'telecom/ispgroup_list.html'
    page_number = request.GET.get('page', '')
    paginator = Paginator(queryset, paginate_by)
    page_obj = paginator.get_page(page_number)
    is_paginated = page_number.lower() != 'all' and page_obj.has_other_pages()
    context = {
        'model': model,
        'page_obj': page_obj,
        'object_list': page_obj if is_paginated else queryset,
        'is_paginated': is_paginated,
    }
    return render(request, template_name, context)


@login_required
@permission_required('telecom.add_ispgroup', raise_exception=True, exception=Http404)
def ispgroup_create(request):
    model = IspGroup
    instance = model(created_by=request.user)
    form_class = IspGroupModelForm
    success_url = reverse('telecom:ispgroup_list')
    form_buttons = ['create']
    template_name = 'telecom/ispgroup_form.html'
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
@permission_required('telecom.change_ispgroup', raise_exception=True, exception=Http404)
def ispgroup_update(request, pk):
    model = IspGroup
    queryset = get_ispgroup_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk)
    form_class = IspGroupModelForm
    success_url = reverse('telecom:ispgroup_list')
    form_buttons = ['update']
    template_name = 'telecom/ispgroup_form.html'
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class(instance=instance)
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)


@login_required
@permission_required('telecom.delete_ispgroup', raise_exception=True, exception=Http404)
def ispgroup_delete(request, pk):
    model = IspGroup
    queryset = get_ispgroup_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk)
    success_url = reverse('telecom:ispgroup_list')
    template_name = 'telecom/ispgroup_confirm_delete.html'
    if request.method == 'POST':
        instance.delete()
        return redirect(success_url)
    context = {'model': model}
    return render(request, template_name, context)


@login_required
@permission_required('telecom.view_prefixlistupdatetask', raise_exception=True, exception=Http404)
def prefixlistupdatetask_list(request):
    model = PrefixListUpdateTask
    queryset = get_prefixlistupdatetask_queryset(request)
    paginate_by = 5
    template_name = 'telecom/prefixlistupdatetask_list.html'
    page_number = request.GET.get('page', '')
    paginator = Paginator(queryset, paginate_by)
    page_obj = paginator.get_page(page_number)
    is_paginated = page_number.lower() != 'all' and page_obj.has_other_pages()
    context = {
        'model': model,
        'page_obj': page_obj,
        'object_list': page_obj if is_paginated else queryset,
        'is_paginated': is_paginated,
    }
    return render(request, template_name, context)


@login_required
@permission_required('telecom.add_prefixlistupdatetask', raise_exception=True, exception=Http404)
def prefixlistupdatetask_create(request):
    model = PrefixListUpdateTask
    instance = model(created_by=request.user)
    form_class = PrefixListUpdateTaskModelForm
    success_url = reverse('telecom:prefixlistupdatetask_list')
    form_buttons = ['create']
    template_name = 'telecom/prefixlistupdatetask_form.html'
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class()
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)


@login_required
@permission_required('telecom.change_prefixlistupdatetask', raise_exception=True, exception=Http404)
def prefixlistupdatetask_update(request, pk):
    model = PrefixListUpdateTask
    queryset = get_prefixlistupdatetask_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk)
    form_class = PrefixListUpdateTaskModelForm
    success_url = reverse('telecom:prefixlistupdatetask_list')
    form_buttons = ['update']
    template_name = 'telecom/prefixlistupdatetask_form.html'
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class(instance=instance)
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)


@login_required
@permission_required('telecom.delete_prefixlistupdatetask', raise_exception=True, exception=Http404)
def prefixlistupdatetask_delete(request, pk):
    model = PrefixListUpdateTask
    queryset = get_prefixlistupdatetask_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk)
    success_url = reverse('telecom:prefixlistupdatetask_list')
    template_name = 'telecom/prefixlistupdatetask_confirm_delete.html'
    if request.method == 'POST':
        instance.delete()
        return redirect(success_url)
    context = {'model': model}
    return render(request, template_name, context)


@login_required
@permission_required('telecom.change_prefixlistupdatetask', raise_exception=True, exception=Http404)
def prefixlistupdatetask_clone(request, pk):
    model = PrefixListUpdateTask
    queryset = get_prefixlistupdatetask_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk)
    instance.pk = None
    instance.created_by = request.user
    form_class = PrefixListUpdateTaskModelForm
    success_url = reverse('telecom:prefixlistupdatetask_list')
    form_buttons = ['update']
    template_name = 'telecom/prefixlistupdatetask_form.html'
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class(instance=instance)
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)


@login_required
@permission_required('telecom.change_prefixlistupdatetask', raise_exception=True, exception=Http404)
def prefixlistupdatetask_previewmailcontent(request, pk):
    model = PrefixListUpdateTask
    queryset = get_prefixlistupdatetask_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk)
    instance.pk = None
    task = model.objects.get(pk=pk)
    file_name = task.loa.name if task.loa.name else None
    ip_type = 'ipv4' if task.ipv4_prefix_list else 'ipv6'
    if task.ipv4_prefix_list and task.ipv6_prefix_list:
        ip_type = 'ipv4 & ipv6'
    ipv4_contents = task.ipv4_prefix_list.split(',\r\n')
    ipv6_contents = task.ipv6_prefix_list.split(',\r\n')
    ispsqs = task.isps.all()
    ispgroupsqs = task.isp_groups.get().isps.all() if task.isp_groups.all() else None
    isps = ispsqs if ispsqs else ispgroupsqs
    if ispsqs and ispgroupsqs:
        isps = (ispsqs | ispgroupsqs).distinct()
    isps = sorted(isps, key=lambda x: x.to == 'unicom@cht.com.tw', reverse=True)
    template_name = 'telecom/mail_content_preview.html'
    context = {'model': model, 'task': task, 'isps': isps, 'ip_type': ip_type, 'ipv4_contents': ipv4_contents, 'ipv6_contents': ipv6_contents, 'file_name': file_name}
    return render(request, template_name, context)


@login_required
@permission_required('telecom.change_prefixlistupdatetask', raise_exception=True, exception=Http404)
def prefixlistupdatetask_sendtaskmail(request, pk):
    model = PrefixListUpdateTask
    task = model.objects.get(pk=pk)
    queryset = get_prefixlistupdatetask_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk)
    file_name = task.loa.name if task.loa.name else None
    ip_type = 'ipv4' if task.ipv4_prefix_list else 'ipv6'
    if task.ipv4_prefix_list and task.ipv6_prefix_list:
        ip_type = 'ipv4 & ipv6'
    ipv4_contents = task.ipv4_prefix_list.split(',\r\n')
    ipv6_contents = task.ipv6_prefix_list.split(',\r\n')
    ispsqs = task.isps.all()
    ispgroupsqs = task.isp_groups.get().isps.all() if task.isp_groups.all() else None
    isps = ispsqs if ispsqs else ispgroupsqs
    if ispsqs and ispgroupsqs:
        isps = (ispsqs | ispgroupsqs).distinct()
    template_name = 'telecom/mail_content.html'
    eng_template_name = 'telecom/eng_mail_content.html'
    template_name_hinet = 'telecom/mail_content_hinet.html'
    hinet_email = 'unicom@cht.com.tw'
    isps_hinet = isps.filter(to=hinet_email)
    isps_other = isps.exclude(to=hinet_email)

    if isps_other:
        for isp in isps_other:
            context = {'model': model, 'task': task, 'isp': isp, 'ip_type': ip_type, 'ipv4_contents': ipv4_contents, 'ipv6_contents': ipv6_contents}
            if isp.eng_mail_type:
                mail_content = render_to_string(eng_template_name, context)
            else:
                mail_content = render_to_string(template_name, context)
            handle_task_mail(isp, task, mail_content)

    if isps_hinet:
        context = {'model': model, 'task': task, 'isps': isps_hinet, 'ip_type': ip_type, 'ipv4_contents': ipv4_contents, 'ipv6_contents': ipv6_contents, 'file_name': file_name}
        mail_content = render_to_string(template_name_hinet, context)
        isp = isps_hinet.first()
        if task.loa:
            path = os.path.join(settings.MEDIA_ROOT, str(task.loa))
            handle_task_mail(isp, task, mail_content, attach_file=path)
        else:
            handle_task_mail(isp, task, mail_content)

    time_now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    instance.meil_sended_time = time_now
    instance.save()
    task_list_url = reverse('telecom:prefixlistupdatetask_list')
    return redirect(task_list_url)

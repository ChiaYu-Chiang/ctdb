from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from core.decorators import permission_required
from core.utils import today

from .forms import DiaryModelForm, DiaryCommentModelForm
from .models import Diary
from news.models import News


def get_diary_queryset(request):
    """
    The queryset of model `Diary` with filter depending on user's role/identity/group.
    The views below will use this as a basic queryset. This ensures that users won't
    accidentally see or touch those they shouldn't.
    """
    model = Diary
    queryset = model.objects.all()
    role = request.user.profile.activated_role
    if not role:
        return queryset.filter(created_by=request.user)
    supervise_roles = role.groupprofile.supervise_roles.all()
    if not supervise_roles:
        return queryset.filter(created_by=request.user)
    return queryset.filter(created_by__groups__in=supervise_roles).distinct()


@login_required
@permission_required('diary.view_diary', raise_exception=True, exception=Http404)
def diary_list(request):
    model = Diary
    queryset = get_diary_queryset(request)
    paginate_by = 5
    template_name = 'diary/diary_list.html'
    page_number = request.GET.get('page', '')
    dep = request.GET.get('dep')
    queryset = queryset.filter(created_by__groups__name=dep) if dep else queryset
    role = request.user.profile.activated_role
    supervise_roles = role.groupprofile.supervise_roles.all() if role else None
    paginator = Paginator(queryset, paginate_by)
    page_obj = paginator.get_page(page_number)
    is_paginated = page_number.lower() != 'all' and page_obj.has_other_pages()

    is_pinned_news = News.objects.filter(is_pinned=True, created_by_id__in=[10, 1003, 1004])  # 10:Vicky

    context = {
        'model': model,
        'page_obj': page_obj,
        'object_list': page_obj if is_paginated else queryset,
        'is_paginated': is_paginated,
        'supervise_roles': supervise_roles,
        'is_pinned_news': is_pinned_news,
    }
    return render(request, template_name, context)


@login_required
@permission_required('diary.add_diary', raise_exception=True, exception=Http404)
def diary_create(request):
    model = Diary
    instance = model(created_by=request.user)
    form_class = DiaryModelForm
    success_url = reverse('diary:diary_list')
    form_buttons = ['create', 'save_and_continue_editing']
    template_name = 'diary/diary_form.html'
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        if form.is_valid():
            instance = form.save()
            if request.POST.get('save_and_continue_editing'):
                return redirect(reverse('diary:diary_update', kwargs={'pk': instance.pk}))
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class()
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)


@login_required
@permission_required('diary.change_diary', raise_exception=True, exception=Http404)
def diary_update(request, pk):
    model = Diary
    queryset = get_diary_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk, created_by=request.user)
    form_class = DiaryModelForm
    success_url = reverse('diary:diary_list')
    form_buttons = ['update', 'save_and_continue_editing']
    template_name = 'diary/diary_form.html'
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        if form.is_valid():
            instance = form.save()
            if request.POST.get('save_and_continue_editing'):
                return redirect(reverse('diary:diary_update', kwargs={'pk': instance.pk}))
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class(instance=instance)
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)


@login_required
@permission_required('diary.change_diary', raise_exception=True, exception=Http404)
def diary_comment(request, pk):
    model = Diary
    queryset = get_diary_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk)  # supervisor needed
    form_class = DiaryCommentModelForm
    success_url = reverse('diary:diary_list')
    form_buttons = ['update']
    template_name = 'diary/diary_form.html'
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        if form.is_valid():
            instance = form.save()
            return redirect(success_url)
        context = {'model': model, 'form': form, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class(instance=instance)
    context = {'model': model, 'form': form, 'form_buttons': form_buttons}
    return render(request, template_name, context)


@login_required
@permission_required('diary.delete_diary', raise_exception=True, exception=Http404)
def diary_delete(request, pk):
    model = Diary
    queryset = get_diary_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk, created_by=request.user)
    success_url = reverse('diary:diary_list')
    template_name = 'diary/diary_confirm_delete.html'
    if request.method == 'POST':
        instance.delete()
        return redirect(success_url)
    context = {'model': model}
    return render(request, template_name, context)


@login_required
@permission_required('diary.change_diary', raise_exception=True, exception=Http404)
def diary_clone(request, pk):
    model = Diary
    queryset = get_diary_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk, created_by=request.user)
    instance.pk = None
    instance.comment = ''
    instance.date = today()
    form_class = DiaryModelForm
    success_url = reverse('diary:diary_list')
    form_buttons = ['create']
    template_name = 'diary/diary_form.html'
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

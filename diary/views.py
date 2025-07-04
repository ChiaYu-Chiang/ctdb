from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone

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
    dep = request.GET.get('dep', '')
    member = request.GET.get('member', '')
    search_input = request.GET.get('search_input', '')
    queryset = queryset.filter(created_by__groups__name=dep) if dep else queryset
    queryset = queryset.filter(created_by__username=member) if member else queryset
    if search_input:
        queryset = queryset.filter(
            Q(created_by__username__icontains=search_input) |
            Q(daily_record__icontains=search_input) |
            Q(todo__icontains=search_input) |
            Q(date__icontains=search_input) |
            Q(daily_check__icontains=search_input) |
            Q(remark__icontains=search_input) |
            Q(comment__icontains=search_input)
        )
    role = request.user.profile.activated_role
    supervise_roles = role.groupprofile.supervise_roles.all() if role else None
    dep_role = supervise_roles.filter(name=dep).first() if supervise_roles else None
    supervise_members = dep_role.user_set.filter(is_active=True) if dep_role else None
    paginator = Paginator(queryset, paginate_by)
    page_obj = paginator.get_page(page_number)
    is_paginated = page_number.lower() != 'all' and page_obj.has_other_pages()

    today = timezone.now().date()
    is_pinned_news = News.objects.filter(
        Q(created_by_id__in=[1023, 1006, 1004]) &
        Q(is_pinned=True) &
        (Q(due__isnull=True) | Q(due__date__gte=today))
    )

    context = {
        'model': model,
        'page_obj': page_obj,
        'object_list': page_obj if is_paginated else queryset,
        'is_paginated': is_paginated,
        'supervise_roles': supervise_roles,
        'supervise_members': supervise_members,
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

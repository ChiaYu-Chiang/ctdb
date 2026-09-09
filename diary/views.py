from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone

from core.decorators import permission_required
from core.utils import today

from .forms import DiaryModelForm, DiaryCommentModelForm, DiaryWorkHourFormSet
from .models import Diary
from news.models import News


# I02 member/supervisor are currently the only roles that record work hours.
# I00 supervisor (who oversees I02 among other departments) intentionally does
# NOT count as i02 here, so the "母部門主管" never sees the work-hours column.
I02_ROLE_NAMES = ('I02 member', 'I02 supervisor')


def is_i02_role(role):
    return bool(role) and role.name in I02_ROLE_NAMES


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
    role = request.user.profile.activated_role
    show_work_hours = is_i02_role(role)
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
            Q(comment__icontains=search_input) |
            Q(work_hours__order_number__icontains=search_input) |
            Q(work_hours__customer_name__icontains=search_input) |
            Q(work_hours__sales_rep__icontains=search_input) |
            Q(work_hours__product_category__icontains=search_input) |
            Q(work_hours__requirement__icontains=search_input) |
            Q(work_hours__handling_content__icontains=search_input)
        ).distinct()  # `work_hours` is a to-many relation; dedupe rows matched via more than one item.
    supervise_roles = role.groupprofile.supervise_roles.all() if role else None
    dep_role = supervise_roles.filter(name=dep).first() if supervise_roles else None
    supervise_members = dep_role.user_set.filter(is_active=True) if dep_role else None
    paginator = Paginator(queryset, paginate_by)
    page_obj = paginator.get_page(page_number)
    is_paginated = page_number.lower() != 'all' and page_obj.has_other_pages()

    # Renamed from `today` to avoid shadowing the `core.utils.today` import used elsewhere in this module.
    today_date = timezone.now().date()
    is_pinned_news = News.objects.filter(
        Q(created_by_id__in=[1023, 1006, 1004]) &
        Q(is_pinned=True) &
        (Q(due__isnull=True) | Q(due__date__gte=today_date)) &
        (Q(visible_due__isnull=True) | Q(visible_due__date__gte=today_date))
    )

    context = {
        'model': model,
        'page_obj': page_obj,
        'object_list': page_obj if is_paginated else queryset,
        'is_paginated': is_paginated,
        'supervise_roles': supervise_roles,
        'supervise_members': supervise_members,
        'is_pinned_news': is_pinned_news,
        'show_work_hours': show_work_hours,
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
    role = request.user.profile.activated_role
    is_i02 = is_i02_role(role)
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        formset = DiaryWorkHourFormSet(data=request.POST, instance=instance) if is_i02 else None
        if form.is_valid() and (formset is None or formset.is_valid()):
            with transaction.atomic():
                instance = form.save()
                if formset is not None:
                    formset.instance = instance
                    formset.save()
            if request.POST.get('save_and_continue_editing'):
                return redirect(reverse('diary:diary_update', kwargs={'pk': instance.pk}))
            return redirect(success_url)
        context = {'model': model, 'form': form, 'formset': formset, 'is_i02': is_i02, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class()
    formset = DiaryWorkHourFormSet(instance=instance) if is_i02 else None
    context = {'model': model, 'form': form, 'formset': formset, 'is_i02': is_i02, 'form_buttons': form_buttons}
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
    role = request.user.profile.activated_role
    is_i02 = is_i02_role(role)
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        formset = DiaryWorkHourFormSet(data=request.POST, instance=instance) if is_i02 else None
        if form.is_valid() and (formset is None or formset.is_valid()):
            with transaction.atomic():
                instance = form.save()
                if formset is not None:
                    formset.instance = instance
                    formset.save()
            if request.POST.get('save_and_continue_editing'):
                return redirect(reverse('diary:diary_update', kwargs={'pk': instance.pk}))
            return redirect(success_url)
        context = {'model': model, 'form': form, 'formset': formset, 'is_i02': is_i02, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class(instance=instance)
    formset = DiaryWorkHourFormSet(instance=instance) if is_i02 else None
    context = {'model': model, 'form': form, 'formset': formset, 'is_i02': is_i02, 'form_buttons': form_buttons}
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
    role = request.user.profile.activated_role
    is_i02 = is_i02_role(role)
    # Grab the source diary's work-hour items *before* we blank out the pk below,
    # so they can be offered as a pre-filled starting point for the new entry.
    source_work_hour_initial = [
        {
            'order_number': work_hour.order_number,
            'customer_name': work_hour.customer_name,
            'sales_rep': work_hour.sales_rep,
            'product_category': work_hour.product_category,
            'requirement': work_hour.requirement,
            'handling_content': work_hour.handling_content,
            'hours': work_hour.hours,
        }
        for work_hour in instance.work_hours.all()
    ] if is_i02 else []
    instance.pk = None
    instance.comment = ''
    instance.date = today()
    form_class = DiaryModelForm
    success_url = reverse('diary:diary_list')
    form_buttons = ['create']
    template_name = 'diary/diary_form.html'
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        formset = DiaryWorkHourFormSet(data=request.POST, instance=instance) if is_i02 else None
        if form.is_valid() and (formset is None or formset.is_valid()):
            with transaction.atomic():
                instance = form.save()
                if formset is not None:
                    formset.instance = instance
                    formset.save()
            return redirect(success_url)
        context = {'model': model, 'form': form, 'formset': formset, 'is_i02': is_i02, 'form_buttons': form_buttons}
        return render(request, template_name, context)
    form = form_class(instance=instance)
    formset = None
    if is_i02:
        # `instance` isn't saved yet, so a formset bound to it has zero existing rows;
        # use `initial` + a matching `extra` count to pre-fill the previous day's items.
        formset = DiaryWorkHourFormSet(instance=Diary(), initial=source_work_hour_initial)
        formset.extra = max(len(source_work_hour_initial), 1)
    context = {'model': model, 'form': form, 'formset': formset, 'is_i02': is_i02, 'form_buttons': form_buttons}
    return render(request, template_name, context)
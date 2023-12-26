from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from core.decorators import permission_required

from .forms import NewsModelForm
from .models import News


def get_dep_news_queryset(request):
    """
    The queryset of model `Reminder` with filter depending on user's role/identity/group.
    The views below will use this as a basic queryset. This ensures that users won't
    accidentally see or touch those they shouldn't.
    """
    model = News
    queryset = model.objects.exclude(created_by_id__in=[10, 1006, 1004])
    role = request.user.profile.activated_role
    deps = request.user.groups.filter(groupprofile__is_department=True)
    if not role:
        return queryset.filter(created_by__groups__in=deps).distinct()
    supervise_roles = role.groupprofile.supervise_roles.all()
    if not supervise_roles:
        return queryset.filter(created_by__groups__in=deps).distinct()
    return queryset.filter(created_by__groups__in=supervise_roles).distinct()


@login_required
def news_list(request):
    model = News
    paginate_by = 5
    template_name = 'news/news_list.html'
    is_supervisor = True
    qs = News.objects.filter(created_by_id__in=[10, 1006, 1004])  # ID:10 == Vicky, 1006 == jill, 1004 == brian
    page_number = request.GET.get('page', '')
    paginator = Paginator(qs, paginate_by)
    page_obj = paginator.get_page(page_number)
    is_paginated = page_number.lower() != 'all' and page_obj.has_other_pages()
    context = {
        'model': model,
        'page_obj': page_obj,
        'object_list': page_obj if is_paginated else qs,
        'is_paginated': is_paginated,
        'is_supervisor': is_supervisor,
    }
    return render(request, template_name, context)


@login_required
def dep_news_list(request):
    model = News
    qs = get_dep_news_queryset(request)
    paginate_by = 5
    template_name = 'news/dep_news_list.html'
    is_supervisor = True
    dep = request.GET.get('dep')
    qs = qs.filter(created_by__groups__name=dep) if dep else qs
    role = request.user.profile.activated_role
    supervise_roles = role.groupprofile.supervise_roles.all() if role else None
    page_number = request.GET.get('page', '')
    paginator = Paginator(qs, paginate_by)
    page_obj = paginator.get_page(page_number)
    is_paginated = page_number.lower() != 'all' and page_obj.has_other_pages()
    context = {
        'model': model,
        'page_obj': page_obj,
        'object_list': page_obj if is_paginated else qs,
        'is_paginated': is_paginated,
        'is_supervisor': is_supervisor,
        'supervise_roles': supervise_roles,
    }
    return render(request, template_name, context)


@login_required
@permission_required('news.add_news', raise_exception=True, exception=Http404)
def news_create(request):
    model = News
    instance = model(created_by=request.user)
    form_class = NewsModelForm
    success_url1 = reverse('news:news_list')
    success_url2 = reverse('news:dep_news_list')
    success_url = success_url1 if request.user.username == 'vicky_lin' or 'jill_ko' or 'Brian_Chiang' else success_url2
    form_buttons = ['create']
    template_name = 'news/news_form.html'
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
@permission_required('news.change_news', raise_exception=True, exception=Http404)
def news_update(request, pk):
    model = News
    instance = get_object_or_404(klass=model, pk=pk, created_by=request.user)
    form_class = NewsModelForm
    success_url1 = reverse('news:news_list')
    success_url2 = reverse('news:dep_news_list')
    success_url = success_url1 if request.user.username == 'vicky_lin' or 'jill_ko' or 'Brian_Chiang' else success_url2
    form_buttons = ['update']
    template_name = 'news/news_form.html'
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
@permission_required('news.delete_news', raise_exception=True, exception=Http404)
def news_delete(request, pk):
    model = News
    instance = get_object_or_404(klass=model, pk=pk, created_by=request.user)
    success_url1 = reverse('news:news_list')
    success_url2 = reverse('news:dep_news_list')
    success_url = success_url1 if request.user.username == 'vicky_lin' or 'jill_ko' or 'Brian_Chiang' else success_url2
    template_name = 'news/news_confirm_delete.html'
    if request.method == 'POST':
        instance.delete()
        return redirect(success_url)
    context = {'model': model}
    return render(request, template_name, context)

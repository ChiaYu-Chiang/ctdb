from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import Http404
from django.shortcuts import render

from core.decorators import permission_required

from .models import Log

User = get_user_model()


def get_diary_log_queryset(request):
    """
    The queryset of model `Log` with filter depending on user's role/identity/group.
    The views below will use this as a basic queryset. This ensures that users won't
    accidentally see or touch those they shouldn't.
    """
    model = Log
    queryset = model.objects.all().filter(model_name='diary')
    role = request.user.profile.activated_role
    if not role:
        return queryset.filter(model_name='diary', created_by=request.user)
    supervise_roles = role.groupprofile.supervise_roles.all()
    if not supervise_roles:
        return queryset.filter(model_name='diary', created_by=request.user)
    return queryset.filter(created_by__groups__in=supervise_roles).distinct()


def get_pilotadmin_log_queryset(request):
    model = Log
    queryset = model.objects.all().filter(model_name='pilotadmin')

    return queryset



@login_required
@permission_required('log.view_log', raise_exception=True, exception=Http404)
def diary_log_list(request):
    model = Log
    queryset = get_diary_log_queryset(request)
    paginate_by = 5
    template_name = 'log/diary_log_list.html'
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
@permission_required('pilotadmin.view_pilotadmin', raise_exception=True, exception=Http404)
def pilotadmin_log_list(request):
    model = Log
    queryset = get_pilotadmin_log_queryset(request)
    paginate_by = 10
    template_name = 'log/diary_log_list.html'
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
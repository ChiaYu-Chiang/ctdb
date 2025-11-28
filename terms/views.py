from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from core.decorators import permission_required

from .forms import TermsModelForm
from .models import Terms

def get_all_terms_queryset(request):
    """
    The queryset of model `Terms` with filter depending on user's role/identity/group.
    The views below will use this as a basic queryset. This ensures that users won't
    accidentally see or touch those they shouldn't.
    """
    model = Terms
    queryset = model.objects.all()
    return queryset


@login_required
@permission_required('terms.view_terms', raise_exception=True, exception=Http404)
def terms_list(request):
    model = Terms
    queryset = get_all_terms_queryset(request)
    paginate_by = 5
    template_name = 'terms/terms_list.html'
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
@permission_required('terms.add_terms', raise_exception=True, exception=Http404)
def terms_create(request):
    model = Terms
    instance = model(created_by=request.user)
    form_class = TermsModelForm
    success_url = reverse('terms:terms_list')
    form_buttons = ['create']
    template_name = 'terms/terms_form.html'
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
@permission_required('terms.change_terms', raise_exception=True, exception=Http404)
def terms_update(request, pk):
    model = Terms
    queryset = get_all_terms_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk, created_by=request.user)
    form_class = TermsModelForm
    success_url = reverse('terms:terms_list')
    form_buttons = ['update']
    template_name = 'terms/terms_form.html'
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
@permission_required('terms.delete_terms', raise_exception=True, exception=Http404)
def terms_delete(request, pk):
    model = Terms
    queryset = get_all_terms_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk, created_by=request.user)
    success_url = reverse('terms:terms_list')
    template_name = 'terms/terms_confirm_delete.html'
    if request.method == 'POST':
        instance.delete()
        return redirect(success_url)
    context = {'model': model}
    return render(request, template_name, context)
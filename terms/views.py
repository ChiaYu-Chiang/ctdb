from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from core.decorators import permission_required

from .forms import TermsModelForm
from .models import Terms

from pypinyin import lazy_pinyin, Style

import pandas as pd
from django.contrib import messages
from django.http import HttpResponse

ALPHABET = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ['#']


def get_all_terms_queryset(request):
    model = Terms
    queryset = model.objects.all()
    return queryset


def generate_sort_key(term):
    if not term.short_name:
        return ""
    first_char = term.short_name.strip()[0]
    if '\u4e00' <= first_char <= '\u9fff':
        bopomofo_list = lazy_pinyin(term.short_name, style=Style.BOPOMOFO)
        bopomofo_str = "".join(bopomofo_list)
        return f"z_{bopomofo_str}"
    else:
        return f"a_{term.short_name.lower()}"


def get_first_letter(short_name):
    """
    Return the uppercase first letter for index purposes.
    - ASCII alpha first char -> that letter
    - CJK first char -> first letter of its pinyin romanization
    - Anything else -> '#'
    """
    if not short_name:
        return '#'
    first = short_name.strip()[0]
    if first.isalpha() and first.isascii():
        return first.upper()
    if '\u4e00' <= first <= '\u9fff':
        pinyin_list = lazy_pinyin(first)
        if pinyin_list and pinyin_list[0]:
            pinyin_first = pinyin_list[0][0].upper()
            if pinyin_first.isalpha():
                return pinyin_first
    return '#'


@login_required
@permission_required('terms.view_terms', raise_exception=True, exception=Http404)
def terms_list(request):
    model = Terms
    queryset = get_all_terms_queryset(request)

    # --- Search / filter params ---
    active_letter = request.GET.get('letter', '').upper()
    search_query = request.GET.get('q', '').strip()

    # Mutual exclusion: if both somehow arrive, letter takes priority
    if active_letter:
        search_query = ''
        if active_letter == '#':
            terms_qs = [t for t in queryset if get_first_letter(t.short_name) == '#']
        else:
            terms_qs = [t for t in queryset if get_first_letter(t.short_name) == active_letter]
    elif search_query:
        terms_qs = list(
            queryset.filter(
                Q(short_name__icontains=search_query) |
                Q(full_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(management_department__icontains=search_query) |
                Q(domain_category__icontains=search_query)
            )
        )
    else:
        terms_qs = list(queryset)

    sorted_terms_list = sorted(terms_qs, key=generate_sort_key)

    # Letters that have at least one term in the full DB
    all_short_names = list(queryset.values_list('short_name', flat=True))
    available_letters = set(get_first_letter(n) for n in all_short_names)

    paginate_by = 12  # 12 cards = 6 rows × 2 columns
    template_name = 'terms/terms_list.html'
    page_number = request.GET.get('page', '')
    paginator = Paginator(sorted_terms_list, paginate_by)
    page_obj = paginator.get_page(page_number)
    is_paginated = page_number.lower() != 'all' and page_obj.has_other_pages()

    context = {
        'model': model,
        'page_obj': page_obj,
        'object_list': page_obj if is_paginated else sorted_terms_list,
        'is_paginated': is_paginated,
        'alphabet': ALPHABET,
        'available_letters': available_letters,
        'active_letter': active_letter,
        'search_query': search_query,
        'total_count': len(sorted_terms_list),
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


@login_required
@permission_required('terms.add_terms', raise_exception=True, exception=Http404)
def download_template(request):
    columns = ['Short Name', 'Full Name', 'URL', 'Management Department', 'Domain Category', 'Description']
    df = pd.DataFrame(columns=columns)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="terms_template.xlsx"'
    df.to_excel(response, index=False, engine='openpyxl')
    return response


@login_required
@permission_required('terms.add_terms', raise_exception=True, exception=Http404)
def terms_import(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            messages.error(request, '請選擇要上傳的檔案。')
            return redirect('terms:terms_list')
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, '檔案格式錯誤，請上傳 .xlsx 檔案。')
            return redirect('terms:terms_list')
        try:
            df = pd.read_excel(excel_file, engine='openpyxl')
            expected_columns = ['Short Name', 'Full Name', 'URL', 'Management Department', 'Domain Category', 'Description']
            if not all(col in df.columns for col in expected_columns):
                messages.error(request, 'Excel 欄位不符，請下載最新範本使用。')
                return redirect('terms:terms_list')
            df = df.fillna('')
            terms_to_create = []
            for index, row in df.iterrows():
                if row['Short Name'] and row['Full Name']:
                    terms_to_create.append(
                        Terms(
                            short_name=str(row['Short Name']).strip(),
                            full_name=str(row['Full Name']).strip(),
                            url=str(row['URL']).strip() if row['URL'] else None,
                            management_department=str(row['Management Department']).strip(),
                            domain_category=str(row['Domain Category']).strip(),
                            description=str(row['Description']).strip(),
                            created_by=request.user
                        )
                    )
            if terms_to_create:
                Terms.objects.bulk_create(terms_to_create)
                messages.success(request, f'成功匯入 {len(terms_to_create)} 筆專有名詞！')
            else:
                messages.warning(request, '沒有找到有效的資料可以匯入，請確認 Excel 內容。')
        except Exception as e:
            messages.error(request, f'匯入失敗，發生錯誤：{str(e)}')
    return redirect('terms:terms_list')
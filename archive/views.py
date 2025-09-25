from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import pandas as pd
from datetime import timedelta
from django.contrib import messages

from core.decorators import permission_required
from reminder.models import Reminder

from .forms import ArchiveModelForm
from .models import Archive


def get_all_archive_queryset(request):
    """
    The queryset of model `Archive` with filter depending on user's role/identity/group.
    The views below will use this as a basic queryset. This ensures that users won't
    accidentally see or touch those they shouldn't.
    """
    model = Archive
    queryset = model.objects.all()
    return queryset


# 一般檔案
def get_archive_queryset(request):
    """
    The queryset of model `Archive` with filter depending on user's role/identity/group.
    The views below will use this as a basic queryset. This ensures that users won't
    accidentally see or touch those they shouldn't.
    """
    model = Archive
    queryset = model.objects.filter(type="files")
    return queryset


# 月刊專區
def get_journals_queryset(request):
    """
    The queryset of model `Archive` with filter depending on user's role/identity/group.
    The views below will use this as a basic queryset. This ensures that users won't
    accidentally see or touch those they shouldn't.
    """
    model = Archive
    queryset = model.objects.filter(type='journals')
    return queryset


# 處級佈達專區
def get_announce_queryset(request):
    """
    The queryset of model `Archive` with filter depending on user's role/identity/group.
    The views below will use this as a basic queryset. This ensures that users won't
    accidentally see or touch those they shouldn't.
    """
    model = Archive
    queryset = model.objects.filter(type='announce')
    return queryset


def get_department_email(department_code):
    """根據部門代碼取得群組郵件"""
    # 部門郵箱對應表
    department_emails = {
        'I00': [
            'i00@chief.com.tw',
            'i00_manager@chief.com.tw',
            'gino_kao@chief.com.tw',
            'kenny_jan@chief.com.tw',
            'morris_fu@chief.com.tw',
            'aaron_lin@chief.com.tw',
            'ryan_hsiao@chief.com.tw',
            'eric_wu@chief.com.tw',
            'hank_tsai@chief.com.tw',
            'louis_wen@chief.com.tw',
            'ken@chief.com.tw',
            'brian_chiang@chief.com.tw',
            'jenny_hung@chief.com.tw'
        ],
        'I01': [
            'i00@chief.com.tw',
            'i01@chief.com.tw'
        ],
        'I02': [
            'i00@chief.com.tw',
            'i02@chief.com.tw'
        ],
        'I03': [
            'i00@chief.com.tw',
            'i03@chief.com.tw'
        ],
        'I04': [
            'i00@chief.com.tw',
            'i04@chief.com.tw'
        ],
        '工程師大會': [
            'i00@chief.com.tw',
            'i01@chief.com.tw',
            'i02@chief.com.tw',
            'i03@chief.com.tw',
            'i04@chief.com.tw'
        ]
    }
    
    # 返回對應的郵箱列表，如果找不到則返回空列表
    return department_emails.get(department_code, [])


@login_required
@permission_required('archive.view_archive', raise_exception=True, exception=Http404)
def archive_list(request):
    model = Archive
    queryset = get_archive_queryset(request)
    paginate_by = 5
    template_name = 'archive/archive_list.html'
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
@permission_required('archive.add_archive', raise_exception=True, exception=Http404)
def archive_create(request):
    model = Archive
    instance = model(created_by=request.user, type='files')
    form_class = ArchiveModelForm
    success_url = reverse('archive:archive_list')
    form_buttons = ['create']
    template_name = 'archive/archive_form.html'
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
@permission_required('archive.change_archive', raise_exception=True, exception=Http404)
def archive_update(request, pk):
    model = Archive
    queryset = get_all_archive_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk, created_by=request.user)
    form_class = ArchiveModelForm
    type = instance.type
    if type == 'files':
        success_url = reverse('archive:archive_list')
    elif type == 'journals':
        success_url = reverse('archive:journals_list')
    elif type == 'announce':
        success_url = reverse('archive:announce_list')
    form_buttons = ['update']
    template_name = 'archive/archive_form.html'
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
@permission_required('archive.delete_archive', raise_exception=True, exception=Http404)
def archive_delete(request, pk):
    model = Archive
    queryset = get_all_archive_queryset(request)
    instance = get_object_or_404(klass=queryset, pk=pk, created_by=request.user)
    type = instance.type
    if type == 'files':
        success_url = reverse('archive:archive_list')
    elif type == 'journals':
        success_url = reverse('archive:journals_list')
    elif type == 'announce':
        success_url = reverse('archive:announce_list')
    template_name = 'archive/archive_confirm_delete.html'
    if request.method == 'POST':
        instance.delete()
        return redirect(success_url)
    context = {'model': model}
    return render(request, template_name, context)


@login_required
@permission_required('archive.view_archive', raise_exception=True, exception=Http404)
def journals_list(request):
    model = Archive
    queryset = get_journals_queryset(request)
    paginate_by = 12
    template_name = 'archive/journals_list.html'
    page_number = request.GET.get('page', '')
    page_number = 'all'
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
@permission_required('archive.add_archive', raise_exception=True, exception=Http404)
def journals_create(request):
    model = Archive
    instance = model(created_by=request.user, type='journals')
    form_class = ArchiveModelForm
    success_url = reverse('archive:journals_list')
    form_buttons = ['create']
    template_name = 'archive/archive_form.html'
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
@permission_required('archive.view_archive', raise_exception=True, exception=Http404)
def announce_list(request):
    model = Archive
    queryset = get_announce_queryset(request)
    paginate_by = 12
    template_name = 'archive/announce_list.html'
    page_number = request.GET.get('page', '')
    page_number = 'all'
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
@permission_required('archive.add_archive', raise_exception=True, exception=Http404)
def announce_create(request):
    model = Archive
    instance = model(created_by=request.user, type='announce')
    form_class = ArchiveModelForm
    success_url = reverse('archive:announce_list')
    form_buttons = ['create']
    template_name = 'archive/archive_form.html'
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
@permission_required('archive.view_archive', raise_exception=True, exception=Http404)
def convert_to_reminders(request, pk):
    """將 Excel 檔案轉換為多個 Reminder"""
    archive = get_object_or_404(Archive, pk=pk)
    success_url = reverse('archive:announce_list')  # 轉換後返回 announce 列表
    
    # 檢查是否可以轉換為 Reminder
    if not archive.can_convert_to_reminders():
        messages.error(request, '此檔案無法轉換為提醒（必須是包含「網應處月會行事曆」的 Excel 檔案）')
        return redirect(success_url)
    
    try:
        # 讀取 Excel 檔案
        df = pd.read_excel(archive.archive.path)
        
        # 使用iloc選擇B、C、D欄位，並重新命名
        selected_columns = df.iloc[:, 1:4]
        selected_columns.columns = ['department', 'meeting_time', 'meeting_room']
        
        # 跳過標題列（第一列）
        selected_columns = selected_columns.iloc[1:]
        
        # 轉換會議時間為datetime格式
        selected_columns['meeting_time'] = pd.to_datetime(selected_columns['meeting_time'])
        
        # 新增提醒時間欄位（會議時間前一週）
        selected_columns['reminder_time'] = selected_columns['meeting_time'] - timedelta(days=7)
        
        reminders_created = 0
        for _, row in selected_columns.iterrows():
            meeting_date = row['meeting_time']
            reminder_date = row['reminder_time']
            department = row['department']
            meeting_room = row['meeting_room']
            
            # 取得參與者郵件
            recipients_list = get_department_email(department)
            recipients = ';'.join(recipients_list) if recipients_list else f'{department.lower()}@chief.com.tw'
            
            # 建立 Reminder
            event_name = department if '工程師大會' in department else f'{department} 月會'
            Reminder.objects.create(
                created_by=request.user,
                event=event_name,
                policy='once',
                start_at=reminder_date.date(),
                end_at=reminder_date.date(),
                email_subject=f'提醒：{event_name} ({meeting_date.strftime("%Y-%m-%d %H:%M")})',
                email_content=f'''親愛的同仁，

提醒您參加以下會議：

• 會議名稱：{event_name}
• 會議時間：{meeting_date.strftime("%Y年%m月%d日 %H:%M")}
• 會議地點：{meeting_room}

請準時參加，謝謝！''',
                recipients=recipients,
                is_active=True
            )
            reminders_created += 1
            
        messages.success(request, f'成功建立 {reminders_created} 個會議提醒')
        
    except Exception as e:
        messages.error(request, f'轉換失敗：{str(e)}')
    
    return redirect(success_url)
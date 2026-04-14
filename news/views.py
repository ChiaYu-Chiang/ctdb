import csv
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http.response import Http404
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


from core.decorators import permission_required

from .forms import NewsModelForm
from .models import News, NewsReadRecord
from django.contrib.auth.models import User

SPECIAL_USERS = ['Apple_Lai', 'jill_ko', 'Brian_Chiang']

def get_dep_news_queryset(request):
    """
    The queryset of model `Reminder` with filter depending on user's role/identity/group.
    The views below will use this as a basic queryset. This ensures that users won't
    accidentally see or touch those they shouldn't.
    """
    model = News
    queryset = model.objects.exclude(created_by__username__in=SPECIAL_USERS)
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
    qs = News.objects.filter(created_by__username__in=SPECIAL_USERS)
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
    success_url = success_url1 if request.user.username in SPECIAL_USERS else success_url2
    form_buttons = ['create']
    template_name = 'news/news_form.html'
    if request.method == 'POST':
        form = form_class(data=request.POST, instance=instance)
        if form.is_valid():
            news = form.save()
            news_title = news.title

            if success_url == success_url1:
                active_users = User.objects.filter(is_active=1)
                recipient_list = [user.email for user in active_users if user.email]
                send_mail(
                    subject=f"[TDB] 最新消息：{news_title}",
                    message=f"TDB最新消息已發布：{news_title}。\n\n請至TDB最新消息專區查看最新發布公告。",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipient_list,
                    fail_silently=False,
                    html_message=f"TDB最新消息已發布：{news_title}。\n\n請至<a href='https://tdb.chief-tech.net/news/'>最新消息</a>查看最新發布公告。",
                )

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
    success_url = success_url1 if request.user.username in SPECIAL_USERS else success_url2
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
    success_url = success_url1 if request.user.username in SPECIAL_USERS else success_url2
    template_name = 'news/news_confirm_delete.html'
    if request.method == 'POST':
        instance.delete()
        return redirect(success_url)
    context = {'model': model}
    return render(request, template_name, context)


@login_required
def news_sign_in(request, pk):
    news = get_object_or_404(News, pk=pk)
    NewsReadRecord.objects.get_or_create(news=news, user=request.user)
    
    previous_url = request.META.get('HTTP_REFERER')
    if previous_url:
        return redirect(previous_url)

    return redirect('news:news_list')


@login_required
def news_read_report(request, pk):
    news = get_object_or_404(News, pk=pk)
    role = request.user.profile.activated_role

    if not role and request.user.username not in SPECIAL_USERS:
        return HttpResponseForbidden(_('You have no permission to read this list.'))

    supervise_roles = []
    if role:
        supervise_roles = role.groupprofile.supervise_roles.all()
    
    # 1. 先取得這篇公告「已簽到」的使用者 ID 列表
    read_user_ids = NewsReadRecord.objects.filter(news=news).values_list('user_id', flat=True)
    
    if request.user.username in SPECIAL_USERS:
        # 特權帳號：看全部的已簽到與未簽到紀錄
        records = NewsReadRecord.objects.filter(news=news).select_related('user__profile')
        # 排除已簽到的人，即為未簽到的人 (建議加上 is_active=True 排除已離職或停用的帳號)
        unread_users = User.objects.filter(is_active=True).exclude(id__in=read_user_ids).select_related('profile')
        
    elif supervise_roles.exists():
        # 部門/處主管：看轄下群組的已簽到與未簽到紀錄
        records = NewsReadRecord.objects.filter(
            news=news, 
            user__groups__in=supervise_roles
        ).distinct().select_related('user__profile')
        
        # 從 User 中過濾屬於轄下群組的人，並排除已簽到的人
        unread_users = User.objects.filter(
            is_active=True, 
            groups__in=supervise_roles
        ).exclude(id__in=read_user_ids).distinct().select_related('profile')
        
    else:
        return HttpResponseForbidden(_('You have no permission to read this list.'))
    
    context = {
        'news': news,
        'records': records,
        'unread_users': unread_users,  # 將未簽到名單傳入 Template
    }
    return render(request, 'news/read_report.html', context)


@login_required
def news_export_csv(request, pk):
    news = get_object_or_404(News, pk=pk)
    role = request.user.profile.activated_role

    # 1. 權限檢查 (與 read_report 完全相同)
    if not role and request.user.username not in SPECIAL_USERS:
        return HttpResponseForbidden(_('You have no permission to export this list.'))

    supervise_roles = []
    if role:
        supervise_roles = role.groupprofile.supervise_roles.all()
    
    # 2. 撈取資料 (與 read_report 完全相同)
    read_user_ids = NewsReadRecord.objects.filter(news=news).values_list('user_id', flat=True)
    
    if request.user.username in SPECIAL_USERS:
        records = NewsReadRecord.objects.filter(news=news).select_related('user__profile')
        unread_users = User.objects.filter(is_active=True).exclude(id__in=read_user_ids).select_related('profile')
    elif supervise_roles.exists():
        records = NewsReadRecord.objects.filter(news=news, user__groups__in=supervise_roles).distinct().select_related('user__profile')
        unread_users = User.objects.filter(is_active=True, groups__in=supervise_roles).exclude(id__in=read_user_ids).distinct().select_related('profile')
    else:
        return HttpResponseForbidden(_('You have no permission to export this list.'))

    # 3. 建立 CSV 回應
    response = HttpResponse(content_type='text/csv')
    # 設定下載的檔名
    response['Content-Disposition'] = f'attachment; filename="News_SignIn_Report_{news.pk}.csv"'
    
    # 【關鍵】寫入 UTF-8 BOM，防止 Excel 打開中文變亂碼
    response.write('\ufeff'.encode('utf8'))

    writer = csv.writer(response)
    
    # 寫入標題列 (Header)
    writer.writerow(['狀態', '姓名', '簽到時間'])

    # 寫入「已簽到」資料
    for record in records:
        # 將 UTC 時間轉換為本地時間並格式化
        local_time = timezone.localtime(record.read_at).strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow(['已簽到', record.user.username, local_time])

    # 寫入「未簽到」資料
    for user in unread_users:
        writer.writerow(['未簽到', user.username, ''])

    return response
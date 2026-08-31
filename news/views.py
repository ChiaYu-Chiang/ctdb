import csv
from django.conf import settings
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http.response import Http404
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q


from core.decorators import permission_required

from .forms import NewsModelForm
from .models import News, NewsReadRecord
from django.contrib.auth.models import User

SPECIAL_USERS = ['Apple_Lai', 'jill_ko', 'Brian_Chiang']
GLOBAL_REPORT_VIEWERS = ['Brian_Chiang']

def get_dep_news_queryset(request):
    """
    The queryset of model `Reminder` with filter depending on user's role/identity/group.
    The views below will use this as a basic queryset. This ensures that users won't
    accidentally see or touch those they shouldn't.
    """
    model = News
    now = timezone.now()
    valid_condition = Q(is_permanent=True) | Q(is_permanent=False, visible_at__lte=now, visible_due__gte=now)
    queryset = model.objects.exclude(created_by__username__in=SPECIAL_USERS).filter(valid_condition)
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
    now = timezone.now()
    valid_condition = Q(is_permanent=True) | Q(is_permanent=False, visible_at__lte=now, visible_due__gte=now)
    qs = News.objects.filter(created_by__username__in=SPECIAL_USERS).filter(valid_condition)
    page_number = request.GET.get('page', '')
    paginator = Paginator(qs, paginate_by)
    page_obj = paginator.get_page(page_number)
    is_paginated = page_number.lower() != 'all' and page_obj.has_other_pages()
    read_news_ids = NewsReadRecord.objects.filter(user=request.user, news__in=qs).values_list('news_id', flat=True)
    context = {
        'model': model,
        'page_obj': page_obj,
        'object_list': page_obj if is_paginated else qs,
        'is_paginated': is_paginated,
        'is_supervisor': is_supervisor,
        'read_news_ids': list(read_news_ids),
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
    read_news_ids = NewsReadRecord.objects.filter(user=request.user, news__in=qs).values_list('news_id', flat=True)
    context = {
        'model': model,
        'page_obj': page_obj,
        'object_list': page_obj if is_paginated else qs,
        'is_paginated': is_paginated,
        'is_supervisor': is_supervisor,
        'supervise_roles': supervise_roles,
        'read_news_ids': list(read_news_ids)
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
                # send_mail(
                #     subject=f"[TDB] 最新消息：{news_title}",
                #     message=f"TDB最新消息已發布：{news_title}。\n\n請至TDB最新消息專區查看最新發布公告。",
                #     from_email=settings.DEFAULT_FROM_EMAIL,
                #     recipient_list=recipient_list,
                #     fail_silently=False,
                #     html_message=f"TDB最新消息已發布：{news_title}。\n\n請至<a href='https://tdb.chief-tech.net/news/'>最新消息</a>查看最新發布公告。",
                # )

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
    
    if request.user.username in GLOBAL_REPORT_VIEWERS:
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
    
    if request.user.username in GLOBAL_REPORT_VIEWERS:
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


def get_news_deadline(news):
    """
    計算一篇公告的簽閱截止日。
    類型2（時效性）：visible_due
    類型1（標準/永久）：at + 15天
    """
    is_urgent = (
        not news.is_permanent
        and news.visible_at is not None
        and news.visible_due is not None
        and timezone.localtime(news.visible_due).date() < (timezone.localtime(news.visible_at).date() + timedelta(days=15))
    )
    if is_urgent:
        return news.visible_due  # DateTimeField

    if not news.is_permanent and news.visible_at is not None:
        return news.visible_at + timedelta(days=15)  # DateTimeField
    
    return news.at + timedelta(days=15)  # DateTimeField
 
 
@login_required
def news_dashboard(request):
    template_name = 'news/dashboard.html'
    role = request.user.profile.activated_role
    is_global = request.user.username in GLOBAL_REPORT_VIEWERS
 
    # ── 權限檢查（與 news_read_report 相同）──────────────────
    is_authorized = is_global or (
        role is not None and (
            role.name.endswith('supervisor') or
            role.name.endswith('assistant')
        )
    )
    if not is_authorized:
        return HttpResponseForbidden(_('You have no permission to view this page.'))
 
    supervise_roles = []
    if role:
        supervise_roles = list(role.groupprofile.supervise_roles.all())
 
    # ── 基礎：只看 SPECIAL_USERS 發的公告 ───────────────────
    now = timezone.now()
    local_now_dt = timezone.localtime(now)
    year_start = local_now_dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
 
    all_special_news = News.objects.filter(created_by__username__in=SPECIAL_USERS)
 
    # ── 決定「應簽人員」的 User queryset ─────────────────────
    if is_global:
        target_users = User.objects.filter(is_active=True)
    else:
        target_users = User.objects.filter(is_active=True, groups__in=supervise_roles).distinct()
 
    target_user_ids = list(target_users.values_list('id', flat=True))
 
    # ── 計算每篇公告的截止時間，篩出今年內截止的公告 ─────────
    # 為了讓後面的邏輯可以用，先把 deadline 標注在 news 物件上
    news_with_deadline = []
    for news in all_special_news:
        deadline = get_news_deadline(news)
        news.deadline = deadline
        news_with_deadline.append(news)
 
    # 年度範圍：發布時間落在今年 1/1 之後的公告
    current_year = local_now_dt.year
    yearly_news = [n for n in news_with_deadline if timezone.localtime(n.at).year == current_year]
 
    # ── 1-1. 待處理逾期公告數 ────────────────────────────────
    # 截止日已過，且轄下仍有人未簽到
    overdue_news_list = []
    for news in news_with_deadline:
        if news.deadline >= now:
            continue  # 尚未逾期，跳過
        signed_ids = set(
            NewsReadRecord.objects.filter(news=news, user_id__in=target_user_ids)
            .values_list('user_id', flat=True)
        )
        unsigned_count = len([uid for uid in target_user_ids if uid not in signed_ids])
        if unsigned_count > 0:
            news.unsigned_count = unsigned_count
            overdue_news_list.append(news)
 
    pending_overdue_count = len(overdue_news_list)
 
    # ── 1-2. 各部門年度簽閱率 ───────────────────────────────
    # 找出目標部門群組
    from django.contrib.auth.models import Group
    if is_global:
        dept_groups = Group.objects.filter(name__in=['I00', 'I01', 'I02', 'I03', 'I04'])
    else:
        dept_groups = Group.objects.filter(id__in=[g.id for g in supervise_roles])
 
    dept_stats = []
    for dept in dept_groups.order_by('name'):
        dept_users = User.objects.filter(is_active=True, groups=dept)
        dept_user_ids = list(dept_users.values_list('id', flat=True))
 
        total_should_sign = 0   # 總應簽人次
        total_on_time = 0       # 期限內完成人次
 
        for news in yearly_news:
            deadline = news.deadline
            if deadline < year_start:
                continue
            # 這篇公告，這個部門有幾人應簽
            total_should_sign += len(dept_user_ids)
            # 幾人在期限內完成
            on_time_count = NewsReadRecord.objects.filter(
                news=news,
                user_id__in=dept_user_ids,
                read_at__lte=deadline,
            ).count()
            total_on_time += on_time_count
 
        rate = round(total_on_time / total_should_sign * 100) if total_should_sign > 0 else None
        dept_stats.append({
            'name': dept.name.replace(' member', '').replace(' supervisor', '').replace(' assistant', ''),
            'rate': rate,
            'total_should_sign': total_should_sign,
            'total_on_time': total_on_time,
        })
 
    # ── 3. 底部逾期未簽閱次數統計 ───────────────────────────
    # 對每位目標使用者，計算兩種逾期次數
    user_overdue_stats = []
    for user in target_users.select_related('profile').order_by('username'):
        late_signed = 0      # 已補簽但當初超時
        never_signed = 0     # 至今完全沒簽且已過期
 
        for news in news_with_deadline:
            deadline = news.deadline
            if deadline >= now:
                continue  # 尚未逾期的公告不計入
            try:
                record = NewsReadRecord.objects.get(news=news, user=user)
                # 有簽到紀錄，但簽到時間超過截止日
                if record.read_at > deadline:
                    late_signed += 1
            except NewsReadRecord.DoesNotExist:
                # 截止日已過，完全沒簽
                never_signed += 1
 
        if late_signed > 0 or never_signed > 0:
            user_overdue_stats.append({
                'user': user,
                'late_signed': late_signed,
                'never_signed': never_signed,
                'total_overdue': late_signed + never_signed,
            })
 
    context = {
        'pending_overdue_count': pending_overdue_count,
        'dept_stats': dept_stats,
        'overdue_news_list': overdue_news_list,
        'user_overdue_stats': user_overdue_stats,
        'is_global': is_global,
        'supervise_roles': supervise_roles,
    }
    return render(request, template_name, context)

 
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from news.models import News, NewsReadRecord
from news.views import SPECIAL_USERS
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = '每日檢查最新消息簽到狀況（正式發信版本，建議於每日 09:00 執行）'

    def handle(self, *args, **options):
        now_dt = datetime.now()
        
        if now_dt.hour != 9:
            self.stdout.write(f"[{now_dt}] 非執行時間 (09:00)，跳過簽到檢查。")
            return

        self.stdout.write(f"========== [{now_dt}] 開始執行每日簽到檢查與發信作業 ==========")
        
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        active_news = News.objects.filter(created_by__username__in=SPECIAL_USERS)
        active_news = (
            active_news.filter(is_permanent=True) |
            active_news.filter(visible_at__date__lte=today, visible_due__date__gte=today) |
            active_news.filter(is_permanent=False, visible_due__date=yesterday)
        )

        for news in active_news:
            news_date = timezone.localtime(news.visible_at or news.at).date()
            days_passed = (today - news_date).days

            target_departments = ['I00', 'I01', 'I02', 'I03', 'I04']
            read_user_ids = NewsReadRecord.objects.filter(news=news).values_list('user_id', flat=True)
            unsigned_users = User.objects.filter(is_active=True, groups__name__in=target_departments).exclude(id__in=read_user_ids)

            if not unsigned_users.exists():
                continue

            # 判斷公告類型
            is_urgent = (
                not news.is_permanent and
                news.visible_at is not None and
                news.visible_due is not None and
                news.visible_due.date() < (news.visible_at.date() + timedelta(days=15))
            )

            # 類型2：時效性公告
            if is_urgent:
                due_date = news.visible_due.date()

                if today <= due_date:
                    # 上架期間：每日提醒本人
                    remaining_days = (due_date - today).days
                    for user in unsigned_users.exclude(email=''):
                        recipient_format = f"{user.username} <{user.email}>"
                        subject = f"【簽閱提醒】剩餘{remaining_days}天！請儘速簽閱公告：《{news.title}》"
                        message = (
                            f"同仁您好，\n\n"
                            f"提醒您，目前有一則重要公告即將下架，請於今日下班前或截止日前完成確認：《{news.title}》\n\n"
                            f"狀態：尚未簽閱\n"
                            f"截止倒數：預計於 {due_date} 下架，屆時未簽閱者將計入逾期登記。\n\n"
                            f"謝謝您的配合！"
                        )
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[recipient_format],
                            fail_silently=True,
                        )
                    self.stdout.write(f"已發送【時效性公告每日提醒信】給 《{news.title}》 的未簽到者")

                elif today == due_date + timedelta(days=1):
                    # 下架隔天：發主管報表
                    supervisor_reports = {}
                    for user in unsigned_users:
                        user_groups = user.groups.all()
                        supervisors = User.objects.filter(
                            is_active=True,
                            groups__groupprofile__supervise_roles__in=user_groups
                        ).exclude(email='').distinct()
                        for supervisor in supervisors:
                            supervisor_contact = f"{supervisor.username} <{supervisor.email}>"
                            if supervisor_contact not in supervisor_reports:
                                supervisor_reports[supervisor_contact] = set()
                            supervisor_reports[supervisor_contact].add(user.username)

                    for contact_info, usernames in supervisor_reports.items():
                        names_list = sorted(list(usernames))
                        supervisor_name = contact_info.split(' <')[0]
                        subject = f"【TDB最新消息逾期簽閱報表】- 《{news.title}》"
                        message = (
                            f"{supervisor_name}  您好，\n\n"
                            f"以下為逾期未簽閱《{news.title}》之人員名單：\n\n" +
                            "\n".join(names_list)
                        )
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[contact_info],
                            fail_silently=True,
                        )
                    self.stdout.write(f"已發送【時效性公告逾期報表】給 《{news.title}》 的相關主管與幕僚")

                continue  # 類型2處理完畢，不走下面的類型1邏輯

            # 類型1：標準公告 / 永久顯示公告
            if days_passed in [16, 17, 18]:
                remaining_days = 19 - days_passed  # 距主管報表還有幾天：3, 2, 1
                deadline_date = news_date + timedelta(days=19)
                for user in unsigned_users.exclude(email=''):
                    recipient_format = f"{user.username} <{user.email}>"
                    subject = f"【簽閱提醒】剩餘{remaining_days}天！請儘速簽閱公告：《{news.title}》"
                    message = (
                        f"同仁您好，\n\n"
                        f"提醒您，目前有一則重要公告即將截止簽閱，請於今日下班前或截止日前完成確認：《{news.title}》\n\n"
                        f"狀態：尚未簽閱\n"
                        f"截止倒數：預計於 {deadline_date} 截止簽閱，屆時未簽閱者將計入逾期登記。\n\n"
                        f"謝謝您的配合！"
                    )
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient_format],
                        fail_silently=True,
                    )
                self.stdout.write(f"已發送【提醒信】給 《{news.title}》 的未簽到者")

            elif days_passed == 19:
                supervisor_reports = {}
                for user in unsigned_users:
                    user_groups = user.groups.all()
                    supervisors = User.objects.filter(
                        is_active=True,
                        groups__groupprofile__supervise_roles__in=user_groups
                    ).exclude(email='').distinct()
                    for supervisor in supervisors:
                        supervisor_contact = f"{supervisor.username} <{supervisor.email}>"
                        if supervisor_contact not in supervisor_reports:
                            supervisor_reports[supervisor_contact] = set()
                        supervisor_reports[supervisor_contact].add(user.username)

                for contact_info, usernames in supervisor_reports.items():
                    names_list = sorted(list(usernames))
                    supervisor_name = contact_info.split(' <')[0]
                    subject = f"【TDB最新消息逾期簽閱報表】- 《{news.title}》"
                    message = f"{supervisor_name}  您好，\n\n以下為逾期未簽閱《{news.title}》之人員名單：\n\n" + "\n".join(names_list)
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[contact_info],
                        fail_silently=True,
                    )
                self.stdout.write(f"已發送【罰則報表】給 《{news.title}》 的相關主管與幕僚")

        self.stdout.write(f"========== [{datetime.now()}] 簽到檢查與發信作業結束 ==========")
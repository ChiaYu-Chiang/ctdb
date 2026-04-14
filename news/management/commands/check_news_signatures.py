from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail  # 引入發信套件
from news.models import News, NewsReadRecord
from news.views import SPECIAL_USERS
from datetime import datetime

class Command(BaseCommand):
    help = '每日檢查最新消息簽到狀況（正式發信版本，建議於每日 09:00 執行）'

    def handle(self, *args, **options):
        now_dt = datetime.now()
        
        # 配合 autodjangocommand.bat 每小時觸發的機制，只在 9 點執行
        if now_dt.hour != 9:
            self.stdout.write(f"[{now_dt}] 非執行時間 (09:00)，跳過簽到檢查。")
            return

        self.stdout.write(f"========== [{now_dt}] 開始執行每日簽到檢查與發信作業 ==========")
        
        today = timezone.localdate()
        # 只有發布者是 SPECIAL_USERS ('Apple_Lai', 'jill_ko', 'Brian_Chiang') 的公告，才算是「全公司最新消息 (news)」，才會套用簽到罰則
        active_news = News.objects.filter(created_by__username__in=SPECIAL_USERS)

        for news in active_news:
            news_date = timezone.localtime(news.at).date()
            days_passed = (today - news_date).days

            # 定義需要套用罰則機制的目標部門
            target_departments = ['I00', 'I01', 'I02', 'I03', 'I04']
            # 撈出未簽到名單
            read_user_ids = NewsReadRecord.objects.filter(news=news).values_list('user_id', flat=True)
            unsigned_users = User.objects.filter(is_active=True, groups__name__in=target_departments).exclude(id__in=read_user_ids)

            if not unsigned_users.exists():
                continue

            # 狀況 A：期限到後 1~3 天 (第 16, 17, 18 天)，個別發提醒給本人
            if days_passed in [16, 17, 18]:
                # 針對每一個未簽到且有信箱的使用者，進行迴圈處理 (個別發信)
                for user in unsigned_users.exclude(email=''):
                    # 標準的 Email 聯絡人格式： 顯示名稱 <信箱地址>
                    recipient_format = f"{user.username} <{user.email}>"
                    subject = f"【提醒】請盡速簽閱TDB最新消息：《{news.title}》"
                    message = f"{user.username} 您好，\n\nTDB最新消息《{news.title}》的簽閱期限（15天）已過，請盡速登入系統完成簽閱。"
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient_format],
                        fail_silently=True,
                    )
                self.stdout.write(f"已發送【提醒信】給 《{news.title}》 的未簽到者")

            # 狀況 B：期限到後第 4 天 (第 19 天)，發報表給主管/副總/幕僚
            elif days_passed == 19:
                supervisor_reports = {}

                for user in unsigned_users:
                    user_groups = user.groups.all()

                    # 找出管轄這個員工所屬群組的所有「主管/幕僚」帳號
                    supervisors = User.objects.filter(
                        is_active=True,
                        profile__activated_role__groupprofile__supervise_roles__in=user_groups
                    ).exclude(email='').distinct()

                    for supervisor in supervisors:
                        # 將主管的 username 也包進聯絡人格式裡
                        supervisor_contact = f"{supervisor.username} <{supervisor.email}>"
                        
                        if supervisor_contact not in supervisor_reports:
                            supervisor_reports[supervisor_contact] = set()
                        supervisor_reports[supervisor_contact].add(user.username)

                # 寄發專屬的彙整報表給每位主管
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
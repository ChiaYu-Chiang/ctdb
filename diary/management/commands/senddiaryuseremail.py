from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.template import loader

from core.utils import today, date_range
from core.mail import send_mail
from day.models import Day
from diary.models import Diary

User = get_user_model()


class Command(BaseCommand):
    help = 'Commands of notifying users of the diary app.'

    HOLIDAYS = [day.date for day in Day.objects.all() if day.is_holiday]
    EXTRA_WORKDAY = [day.date for day in Day.objects.all() if not day.is_holiday]
    THRESHOLD_LIST = [3, 7, 30]
    SUBJECT_TEMPLATE_NAME = 'diary/mails/diary_missing_notification_subject.txt'
    BODY_TEMPLATE_NAME = 'diary/mails/diary_missing_notification_body.html'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Print messages only. The Email would not be sent.',
        )

    def get_diary_users(self):
        """
        Get all user who need to write diary.
        """
        return User.objects.filter(profile__keep_diary=True)

    def get_diary_needed(self, users):
        """
        Generate a dict with (`user.id`, `date`) as key and boolean value as value.
        This is for recording what kind of diary we need.
        """
        wanted = {}
        for user in users:
            start_date = user.profile.diary_starting_date
            end_date = today()
            dates = date_range(start_date, end_date)
            weekday_dates = [date for date in dates if date.isoweekday() <= 5]
            workday_dates = [date for date in weekday_dates if date not in self.HOLIDAYS]
            wanted_dates = set(workday_dates) | set(self.EXTRA_WORKDAY)
            sorted_wanted_dates = sorted(list(wanted_dates))
            for date in sorted_wanted_dates:
                wanted.update({(user.id, date): False})
        return wanted

    def get_diary_existing(self):
        """
        Generate a dictionary with (`created_by_id`, `date`) as key and boolean value as value.
        This is to recording what kind of diary we have.
        """
        diaries = Diary.objects.all()
        diary_values_list = diaries.values_list('created_by_id', 'date')
        existing = {(values): True for values in diary_values_list}
        return existing

    def get_diary_missing(self, needed, existing):
        """
        Generate a dictionary with `user.id` as key and a list of `date` as value.
        This is to recording what kind of diary we are missing.
        """
        needed.update(existing)
        missing = {}
        for key, value in needed.items():
            if value:
                continue
            user_id, date = key
            if user_id not in missing:
                missing[user_id] = []
            missing[user_id].append(date)
        return missing

    def get_notification_level(self, past_days):
        notification_level = 0
        for threshold in self.THRESHOLD_LIST:
            if past_days >= threshold:
                notification_level += 1
            else:
                break
        return notification_level

    def get_cc(self, user, notification_level):
        cc = []
        while notification_level > 0:
            boss = user.profile.boss
            if boss:
                email = boss.email
                if email:
                    cc.append(boss.email)
                user = boss
            notification_level = notification_level - 1
        return cc

    def send_notification_mail(self, missing, test=True):
        """
        Given a dictionary with `user.id` as key and a list of `date` as value, It
        would send notification Email to those user.
        """
        for user_id, dates in missing.items():
            # Fetch user
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                continue
            # Calculate `notification_level`
            username = user.username
            datestrings = ', '.join(str(date) for date in dates)
            context = {'username': username, 'dates': dates, 'datestrings': datestrings}
            subject = loader.render_to_string(self.SUBJECT_TEMPLATE_NAME, context)
            body = loader.render_to_string(self.BODY_TEMPLATE_NAME, context)
            to = [user.email]

            earliest_date = min(dates)
            past_days = (today() - earliest_date).days
            notification_level = self.get_notification_level(past_days=past_days)

            cc = self.get_cc(user=user, notification_level=notification_level)

            if test:
                pass
            else:
                send_mail(subject=subject, body=body, to=to, cc=cc)

            print('-' * 120)
            print('To:', '; '.join(to))
            print('CC:', '; '.join(cc))
            print(subject)
            print('\n')
            print(body)
            print('-' * 120)

    def handle(self, *args, **options):
        users = self.get_diary_users()
        needed = self.get_diary_needed(users=users)
        existing = self.get_diary_existing()
        missing = self.get_diary_missing(needed=needed, existing=existing)
        if options['test']:
            self.send_notification_mail(missing=missing)
        else:
            self.send_notification_mail(missing=missing, test=False)

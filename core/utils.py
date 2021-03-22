from datetime import timedelta

from django.utils import timezone


def now():
    return timezone.localtime(timezone.now())


def today():
    return timezone.localtime(timezone.now()).date()


def tomorrow():
    return timezone.localtime(timezone.now() + timedelta(days=1)).date()


def remove_unnecessary_seperator(s, seperator):
    if s[-1:] == seperator:
        return s[:-1]
    return s

import json
import os
import time


with open(r'..\..\secrets.json') as f:
    s = f.read()

d = json.loads(s)
PYTHONPATH_ABS = d['PYTHONPATH_ABS']
REPO_ROOT = d['REPO_ROOT']


def calld_django_send_diary_user_email():
    time_string = time.strftime('%Y%m%d%H%M%S')
    print(time_string)
    print('start..')
    cmd = f'{PYTHONPATH_ABS} {REPO_ROOT}\\manage.py senddiaryuseremail'
    os.system(cmd)


def calld_django_send_reminder_email():
    time_string = time.strftime('%Y%m%d%H%M%S')
    print(time_string)
    print('start..')
    cmd = f'{PYTHONPATH_ABS} {REPO_ROOT}\\manage.py sendreminderemail'
    os.system(cmd)


calld_django_send_diary_user_email()
calld_django_send_reminder_email()

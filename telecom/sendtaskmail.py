from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
from django.utils.html import strip_tags


def send_mail(subject, message, from_email, recipient_list, fail_silently=False, auth_user=None, auth_password=None,bcc=None, connection=None,cc=None, html_message=None, attach_file=None):
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    mail = EmailMultiAlternatives(subject, message, from_email, recipient_list, bcc=bcc, connection=connection, cc=cc)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')
    mail.attach_file(attach_file)

    return mail.send()

def handle_task_mail(isp, task, mail_content, attach_file=None, debug=settings.DEBUG):
    seperator = ';'
    recipients = isp.to[:-1] if isp.to[-1:] == seperator else isp.to
    recipient_list = list(map(str.strip, recipients.split(';')))

    recipients_cc = isp.cc[:-1] if isp.cc[-1:] == seperator else isp.cc
    recipient_cc_list = list(map(str.strip, recipients_cc.split(';')))

    recipients_bcc = isp.bcc[:-1] if isp.bcc[-1:] == seperator else isp.bcc
    recipient_bcc_list = list(map(str.strip, recipients_bcc.split(';')))

    if isp.eng_mail_type:
        email_subject = f'[CHIEF TELECOM] -- Please add new BGP entry for our customer - {task.origin_as} {task.subject_warning}'
    else:
        email_subject = f'[是方電訊] -- Please add new BGP entry for our customer - {task.origin_as} {task.subject_warning}'
    email_content = strip_tags(mail_content)

    if debug:
        print("Sending a Email to ", recipient_list)
        print("Sending a Email cc to ", recipient_cc_list)
        print("Email:")
        print(email_subject)
    send_mail(
        email_subject,
        email_content,
        from_email=settings.T21_FROM_MAIL,
        recipient_list=recipient_list,
        bcc=recipient_bcc_list,
        cc=recipient_cc_list,
        html_message=mail_content,
        fail_silently=False,
        attach_file=attach_file
    )

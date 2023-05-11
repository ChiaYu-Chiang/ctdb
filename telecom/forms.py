from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Isp, IspGroup, PrefixListUpdateTask


class IspModelForm(forms.ModelForm):
    customer_no = forms.CharField(
        label=_('Customer No.'),
        widget=forms.Textarea(
            attrs={
                'rows': 2
            }
        ),
        required=False
    )
    cc = forms.CharField(
        label=_('CC'),
        widget=forms.Textarea(
            attrs={
                'placeholder': _(
                    'Please enter one or more Email separated by ";".\n'
                    'For example:\n'
                    '\n'
                    'example1@chief.com.tw;\n'
                    'example2@google.com;\n'
                ),
                'row': 10
            }
        ),
        required=False
    )
    bcc = forms.CharField(
        label=_('BCC'),
        widget=forms.Textarea(
            attrs={
                'placeholder': _(
                    'Please enter one or more Email separated by ";".\n'
                    'For example:\n'
                    '\n'
                    'example1@chief.com.tw;\n'
                    'example2@google.com;\n'
                ),
                'row': 10
            }
        ),
        required=False
    )
    upstream_session_ip = forms.CharField(
        label=_('Upstream Session IP'),
        widget=forms.Textarea(
            attrs={
                'placeholder': _(
                    'Please enter a prefix-list. For example:\n'
                    '\n'
                    '100.100.100.100/24,\n'
                    '100.100.200.100/22 le 24,\n'
                ),
                'rows': 6
            }
        )
    )
    chief_session_ip = forms.CharField(
        label=_('Chief Session IP'),
        widget=forms.Textarea(
            attrs={
                'placeholder': _(
                    'Please enter a prefix-list. For example:\n'
                    '\n'
                    '100.100.100.100/24,\n'
                    '100.100.200.100/22 le 24,\n'
                ),
                'rows': 6
            }
        )
    )
    subject = forms.CharField(
        label=_('Subject'),
        widget=forms.Textarea(
            attrs={
                'placeholder': _(
                    'Create a custom letter subject for this ISP contact.\n'
                    'If left blank, the default template will be used.\n'
                ),
                'rows': 3
            }
        ),
        required=False
    )
    content = forms.CharField(
        label=_('Content'),
        widget=forms.Textarea(
            attrs={
                'placeholder': _(
                    'Create a custom letter content description for this ISP contact.\n'
                    'If left blank, the default template will be used.\n'
                ),
                'rows': 6
            }
        ),
        required=False
    )

    class Meta:
        model = Isp
        exclude = ['created_by', ]


class IspGroupModelForm(forms.ModelForm):

    class Meta:
        model = IspGroup
        exclude = ['created_by', ]


class PrefixListUpdateTaskModelForm(forms.ModelForm):
    ipv4_prefix_list = forms.CharField(
        label=_('IPv4-Prefix-list'),
        widget=forms.Textarea(
            attrs={
                'placeholder': _(
                    'Please enter a prefix-list. For example:\n'
                    '\n'
                    '100.100.100.100/24,\n'
                    '100.100.200.100/22 le 24,\n'
                ),
                'rows': 6
            }
        ),
        required=False
    )
    ipv6_prefix_list = forms.CharField(
        label=_('IPv6-Prefix-list'),
        widget=forms.Textarea(
            attrs={
                'placeholder': _(
                    'Please enter a prefix-list. For example:\n'
                    '\n'
                    '2404:63C0::/32 le 64\n'
                ),
                'rows': 6
            }
        ),
        required=False
    )
    related_ticket = forms.CharField(
        label=_('Related ticket'),
        widget=forms.Textarea(
            attrs={
                'placeholder': _(
                    'Please enter related tickets of this update task, if there is any.'
                ),
                'rows': 3
            }
        ),
        required=False
    )
    loa_remark = forms.CharField(
        label=_('Loa Remark'),
        widget=forms.Textarea(
            attrs={
                'placeholder': _(
                    'The content will appear for HiNet email.'
                ),
                'rows': 3
            }
        ),
        required=False
    )
    remark = forms.CharField(
        label=_('Remark'),
        widget=forms.Textarea(
            attrs={
                'placeholder': _(
                    'Only for the description of the task, the content will not appear in the notification mail.'
                ),
                'rows': 6
            }
        ),
        required=False
    )

    class Meta:
        model = PrefixListUpdateTask
        exclude = ['created_by', 'meil_sended_time']

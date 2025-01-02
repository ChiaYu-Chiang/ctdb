from django import forms
from datetime import datetime
from django.utils.translation import gettext_lazy as _

from .models import Reminder


class ReminderModelForm(forms.ModelForm):
    class Meta:
        model = Reminder
        exclude = ['created_by']
        widgets = {
            'start_at': forms.DateInput(attrs={'type': 'date'}),
            'end_at': forms.DateInput(attrs={'type': 'date'}),
            'specified_dates': forms.Textarea(attrs={
                'rows': 10,
                'placeholder': _(
                    'Please enter one or more specified dates separated by "," and '
                    'the date format must be yyyy-mm-dd. For example:\n'
                    '\n'
                    '2021-03-16,\n'
                    '2021-03-29,\n'
                    '2021-04-01\n'
                ),
            }),
            'recipients': forms.Textarea(attrs={
                'rows': 10,
                'placeholder': _(
                    'Please enter one or more Email separated by ";".\n'
                    'For example:\n'
                    '\n'
                    'example1@chief.com.tw;\n'
                    'example2@google.com;\n'
                ),
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get('start_at')
        end_at = cleaned_data.get('end_at')
        policy = cleaned_data.get('policy')
        if policy == 'specified dates':
            specified_dates = cleaned_data.get('specified_dates')
            if specified_dates:
                date_list = [date.strip() for date in specified_dates.split(',') if date.strip()]
                date_list = [datetime.strptime(date, '%Y-%m-%d').date() for date in date_list]
                if date_list:
                    start_at = min(date_list)
                    end_at = max(date_list)
        elif policy == 'once':
            end_at = start_at
        cleaned_data['start_at'] = start_at
        cleaned_data['end_at'] = end_at
        return cleaned_data

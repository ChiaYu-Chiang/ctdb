from django import forms
from .models import CalendarEvent

class CalendarEventForm(forms.ModelForm):
    support_consultant = forms.MultipleChoiceField(
        choices=CalendarEvent.SUPPORT_CONSULTANT,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Support Consultant"
    )

    class Meta:
        model = CalendarEvent
        fields = ['title', 'support_group', 'support_consultant', 'client_name', 'product_type', 'description', 'start_time', 'end_time', 'participants']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M',),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M',),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field in ['start_time', 'end_time']:
            if self.instance and getattr(self.instance, field):
                self.fields[field].initial = getattr(self.instance, field).strftime('%Y-%m-%dT%H:%M')

        if self.instance and self.instance.pk and self.instance.support_consultant:
            current_consultants = self.instance.support_consultant.split(", ")
            self.fields['support_consultant'].initial = current_consultants

        department = user.profile.activated_role
        if department:
            self.fields['participants'].queryset = department.user_set.filter(is_active=True)
        else:
            self.fields['participants'].queryset = self.fields['participants'].queryset.none()

    def clean_support_consultant(self):
        data = self.cleaned_data.get('support_consultant')
        if data:
            return ", ".join(data)
        return ""
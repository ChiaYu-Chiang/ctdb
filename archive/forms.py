from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Archive


class ArchiveModelForm(forms.ModelForm):
    class Meta:
        model = Archive
        exclude = ['created_by', 'type']
        widgets = {
            'url': forms.URLInput(),
            'visible_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M',),
            'visible_due': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M',),
        }

    def clean(self):
        cleaned_data = super().clean()
        archive = cleaned_data.get('archive')
        url = cleaned_data.get('url')
        is_permanent = cleaned_data.get('is_permanent')
        visible_at = cleaned_data.get('visible_at')
        visible_due = cleaned_data.get('visible_due')

        if not archive and not url:
            self.add_error(None, _('Please upload a file or enter a URL.'))
        if archive and url:
            self.add_error(None, _('Please choose either a file or a URL, not both.'))
        
        if is_permanent is False:
            if not visible_at:
                self.add_error('visible_at', _('If you do not choose to save permanently, you must set a start time.'))
            if not visible_due:
                self.add_error('visible_due', _('If you do not choose to save permanently, you must set an expiration time.'))
            if visible_at and visible_due and visible_at >= visible_due:
                self.add_error('visible_due', _('Expiration time must be later than start time.'))
        return cleaned_data
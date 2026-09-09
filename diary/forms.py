from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Diary, DiaryWorkHour


class DiaryModelForm(forms.ModelForm):
    class Meta:
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'daily_record': forms.Textarea(attrs={'rows': 4, 'class': 'ckeditor4'}),
            'todo': forms.Textarea(attrs={'rows': 4, 'class': 'ckeditor4'}),
            'remark': forms.Textarea(attrs={'rows': 4, 'class': 'ckeditor4'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'ckeditor4', 'readonly': ''}),  # TODO: ckeditor4 or not?
        }
        model = Diary
        exclude = ['created_by']

    def full_clean(self):
        super().full_clean()
        try:
            self.instance.validate_unique()
        except forms.ValidationError:
            self.add_error(field='date', error=_('The diary with this date has already existed.'))


class DiaryCommentModelForm(forms.ModelForm):
    class Meta:
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'readonly': ''}),
            # Attrs readonly & style="pointer-events: none" make the <select> tag work like a readonly field.
            'daily_check': forms.Select(attrs={'readonly': '', 'style': 'pointer-events: none'}),
            'daily_record': forms.Textarea(attrs={'rows': 4, 'class': 'ckeditor4', 'readonly': ''}),
            'todo': forms.Textarea(attrs={'rows': 4, 'class': 'ckeditor4', 'readonly': ''}),
            'remark': forms.Textarea(attrs={'rows': 4, 'class': 'ckeditor4', 'readonly': ''}),
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'ckeditor4'}),  # TODO: ckeditor4 or not?
        }
        model = Diary
        exclude = ['created_by']

    def full_clean(self):
        super().full_clean()
        try:
            self.instance.validate_unique()
        except forms.ValidationError:
            self.add_error(field='date', error=_('The diary with this date has already existed.'))


class DiaryWorkHourForm(forms.ModelForm):
    """
    Single row of the I02 work-hours formset. Strips the free-text fields
    so that e.g. "客戶A" and "客戶A " (trailing space) aren't silently
    treated as different values once this data gets aggregated/reported on.
    """
    STRIPPED_FIELDS = ('order_number', 'customer_name', 'sales_rep', 'product_category', 'requirement', 'handling_content')

    class Meta:
        model = DiaryWorkHour
        fields = ['order_number', 'customer_name', 'sales_rep', 'product_category', 'requirement', 'handling_content', 'hours']
        widgets = {
            'order_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Order number')}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Customer name')}),
            'sales_rep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Sales rep')}),
            'product_category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Product category')}),
            'requirement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Requirement')}),
            'handling_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': _('Handling content')}),
            'hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'placeholder': _('Hours')}),
        }

    def clean(self):
        cleaned_data = super().clean()
        for field_name in self.STRIPPED_FIELDS:
            value = cleaned_data.get(field_name)
            if value:
                cleaned_data[field_name] = value.strip()
        return cleaned_data


# Only instantiated/rendered for I02 diaries (see diary.views.is_i02_role).
DiaryWorkHourFormSet = inlineformset_factory(
    Diary,
    DiaryWorkHour,
    form=DiaryWorkHourForm,
    extra=1,
    can_delete=True,
)
from django import forms

from .models import Terms


class TermsModelForm(forms.ModelForm):
    class Meta:
        model = Terms
        exclude = ['created_by']
from django import forms

from .models import Tool


class ToolModelForm(forms.ModelForm):
    class Meta:
        model = Tool
        exclude = ['created_by']
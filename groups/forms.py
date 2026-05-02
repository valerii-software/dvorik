from django import forms

from .models import Group


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'description', 'avatar')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }

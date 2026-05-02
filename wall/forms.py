from django import forms

from .models import WallComment, WallPost


class WallPostForm(forms.ModelForm):
    class Meta:
        model = WallPost
        fields = ('text',)
        widgets = {'text': forms.Textarea(attrs={
            'placeholder': 'Напишите что-нибудь…',
            'rows': 3,
        })}
        labels = {'text': ''}


class WallCommentForm(forms.ModelForm):
    class Meta:
        model = WallComment
        fields = ('text',)
        widgets = {'text': forms.TextInput(attrs={'placeholder': 'Комментарий…'})}
        labels = {'text': ''}

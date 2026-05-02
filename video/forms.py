from django import forms

from .models import Video


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title', 'description', 'file', 'preview')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'file': forms.ClearableFileInput(attrs={'accept': 'video/*'}),
            'preview': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

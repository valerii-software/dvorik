from django import forms

from .models import AudioTrack


class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = AudioTrack
        fields = ('artist', 'title', 'file')
        widgets = {
            'file': forms.ClearableFileInput(attrs={'accept': 'audio/*'}),
        }

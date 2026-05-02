from django import forms

from .models import Video


MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MiB


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title', 'description', 'file', 'preview')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'file': forms.ClearableFileInput(attrs={'accept': 'video/*'}),
            'preview': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
        help_texts = {
            'file': 'Не более 100 МБ.',
        }

    def clean_file(self):
        f = self.cleaned_data['file']
        if f and getattr(f, 'size', 0) > MAX_VIDEO_SIZE:
            mb = f.size / 1024 / 1024
            raise forms.ValidationError(
                f'Размер файла {mb:.1f} МБ превышает лимит в 100 МБ.'
            )
        return f

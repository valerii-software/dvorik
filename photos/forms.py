from django import forms

from .models import Album, PhotoComment


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ('title', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class PhotoUploadForm(forms.Form):
    images = forms.FileField(
        label='Файлы',
        widget=MultiFileInput(attrs={'multiple': True, 'accept': 'image/*'}),
    )
    description = forms.CharField(
        label='Подпись (для всех)', required=False, max_length=500,
    )

    def clean_images(self):
        # Override default cleaning so all files are returned, not just one.
        files = self.files.getlist('images')
        if not files:
            raise forms.ValidationError('Выберите хотя бы одно изображение.')
        return files


class PhotoCommentForm(forms.ModelForm):
    class Meta:
        model = PhotoComment
        fields = ('text',)
        widgets = {'text': forms.TextInput(attrs={'placeholder': 'Комментарий…'})}
        labels = {'text': ''}

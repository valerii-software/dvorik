from django import forms

from .models import Album, PhotoComment


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ('title', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """FileField that accepts multiple files.

    Django's default FileField rejects a list of UploadedFile objects in
    `to_python`, raising "Ни одного файла не было отправлено". This subclass
    runs the single-file clean over each item — pattern from Django docs.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if not data:
            # Empty list / None -> let parent raise the required error.
            return single_clean(data, initial)
        if isinstance(data, (list, tuple)):
            return [single_clean(d, initial) for d in data]
        return [single_clean(data, initial)]


class PhotoUploadForm(forms.Form):
    images = MultipleFileField(
        label='Файлы',
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'image/*'}),
        error_messages={'required': 'Выберите хотя бы одно изображение.'},
    )
    description = forms.CharField(
        label='Подпись (для всех)', required=False, max_length=500,
    )


class PhotoCommentForm(forms.ModelForm):
    class Meta:
        model = PhotoComment
        fields = ('text',)
        widgets = {'text': forms.TextInput(attrs={'placeholder': 'Комментарий…'})}
        labels = {'text': ''}

from django import forms

from .models import WallComment, WallPost


MAX_WALL_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MiB


class WallPostForm(forms.ModelForm):
    class Meta:
        model = WallPost
        fields = ('text', 'image')
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Напишите что-нибудь…',
                'rows': 3,
            }),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
        labels = {'text': '', 'image': ''}

    def clean_image(self):
        f = self.cleaned_data.get('image')
        if f and getattr(f, 'size', 0) > MAX_WALL_IMAGE_SIZE:
            mb = f.size / 1024 / 1024
            raise forms.ValidationError(
                f'Размер изображения {mb:.1f} МБ превышает лимит в 10 МБ.'
            )
        return f

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('text') and not cleaned.get('image'):
            raise forms.ValidationError('Введите текст или прикрепите изображение.')
        return cleaned


class WallCommentForm(forms.ModelForm):
    class Meta:
        model = WallComment
        fields = ('text',)
        widgets = {'text': forms.TextInput(attrs={'placeholder': 'Комментарий…'})}
        labels = {'text': ''}

from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='Имя', max_length=30)
    last_name = forms.CharField(label='Фамилия', max_length=30)

    class Meta:
        model = Profile
        fields = (
            'avatar', 'gender', 'birth_date', 'marital_status', 'home_city', 'languages',
            'activity', 'interests', 'favourite_music', 'favourite_movies',
            'favourite_books', 'favourite_quotes', 'about',
            'skype', 'icq', 'site',
        )
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'interests': forms.Textarea(attrs={'rows': 2, 'cols': 50}),
            'favourite_music': forms.Textarea(attrs={'rows': 2, 'cols': 50}),
            'favourite_movies': forms.Textarea(attrs={'rows': 2, 'cols': 50}),
            'favourite_books': forms.Textarea(attrs={'rows': 2, 'cols': 50}),
            'favourite_quotes': forms.Textarea(attrs={'rows': 2, 'cols': 50}),
            'about': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.first_name = self.cleaned_data['first_name']
        profile.user.last_name = self.cleaned_data['last_name']
        if commit:
            profile.user.save()
            profile.save()
        return profile

from django.conf import settings
from django.db import models


PRIVACY_CHOICES = [
    ('all', 'все'),
    ('friends', 'только друзья'),
    ('me', 'только я'),
]


class Profile(models.Model):
    GENDER = [('m', 'мужской'), ('f', 'женский'), ('', 'не указан')]
    MARITAL = [
        ('', 'не указано'),
        ('single', 'не женат / не замужем'),
        ('relationship', 'встречается'),
        ('engaged', 'помолвлен(а)'),
        ('married', 'женат / замужем'),
        ('complicated', 'всё сложно'),
        ('searching', 'в активном поиске'),
        ('love', 'влюблён(а)'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    gender = models.CharField('пол', max_length=1, choices=GENDER, blank=True, default='')
    birth_date = models.DateField('день рождения', null=True, blank=True)
    marital_status = models.CharField('сем. положение', max_length=20, choices=MARITAL, blank=True, default='')
    home_city = models.CharField('родной город', max_length=120, blank=True)
    languages = models.CharField('языки', max_length=200, blank=True)

    activity = models.CharField('деятельность', max_length=200, blank=True)
    interests = models.TextField('интересы', blank=True)
    favourite_music = models.TextField('любимая музыка', blank=True)
    favourite_movies = models.TextField('любимые фильмы', blank=True)
    favourite_books = models.TextField('любимые книги', blank=True)
    favourite_quotes = models.TextField('любимые цитаты', blank=True)
    about = models.TextField('о себе', blank=True)

    skype = models.CharField('Skype', max_length=80, blank=True)
    icq = models.CharField('ICQ', max_length=20, blank=True)
    site = models.CharField('сайт', max_length=200, blank=True)

    privacy_profile = models.CharField('кто видит мою страницу', max_length=10,
                                       choices=PRIVACY_CHOICES, default='all')
    privacy_wall_view = models.CharField('кто видит мою стену', max_length=10,
                                         choices=PRIVACY_CHOICES, default='all')
    privacy_wall_post = models.CharField('кто может писать на стену', max_length=10,
                                         choices=PRIVACY_CHOICES, default='all')
    privacy_photos = models.CharField('кто видит мои фотографии', max_length=10,
                                      choices=PRIVACY_CHOICES, default='all')
    privacy_audio = models.CharField('кто видит мои аудиозаписи', max_length=10,
                                     choices=PRIVACY_CHOICES, default='all')
    privacy_video = models.CharField('кто видит мои видеозаписи', max_length=10,
                                     choices=PRIVACY_CHOICES, default='all')
    privacy_groups = models.CharField('кто видит мои группы', max_length=10,
                                      choices=PRIVACY_CHOICES, default='all')
    privacy_messages = models.CharField('кто может писать мне', max_length=10,
                                        choices=PRIVACY_CHOICES, default='all')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'profile<{self.user_id}>'

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/img/no_photo.png'

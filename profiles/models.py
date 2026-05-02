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
    POLITICAL = [
        ('', 'не указаны'),
        ('indifferent', 'безразличные'),
        ('communist', 'коммунистические'),
        ('socialist', 'социалистические'),
        ('moderate', 'умеренные'),
        ('liberal', 'либеральные'),
        ('conservative', 'консервативные'),
        ('monarchist', 'монархические'),
        ('ultraconservative', 'ультраконсервативные'),
        ('libertarian', 'либертарианские'),
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
    political_views = models.CharField('полит. взгляды', max_length=20,
                                       choices=POLITICAL, blank=True, default='')
    religious_views = models.CharField('религ. взгляды', max_length=80, blank=True)
    education = models.CharField('образование', max_length=120, blank=True,
                                 help_text='например: «СПбГУ ’06»')

    activity = models.CharField('деятельность', max_length=200, blank=True)
    interests = models.TextField('интересы', blank=True)
    favourite_music = models.TextField('любимая музыка', blank=True)
    favourite_movies = models.TextField('любимые фильмы', blank=True)
    favourite_tv = models.TextField('любимые телешоу', blank=True)
    favourite_games = models.TextField('любимые игры', blank=True)
    favourite_books = models.TextField('любимые книги', blank=True)
    favourite_quotes = models.TextField('любимые цитаты', blank=True)
    about = models.TextField('о себе', blank=True)

    mobile_phone = models.CharField('мобильный телефон', max_length=40, blank=True)
    skype = models.CharField('Skype', max_length=80, blank=True)
    icq = models.CharField('ICQ', max_length=20, blank=True)
    site = models.CharField('веб-сайт', max_length=200, blank=True)

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

    last_seen = models.DateTimeField(null=True, blank=True, db_index=True)

    now_playing = models.ForeignKey(
        'audio.AudioTrack', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
    )
    now_playing_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'profile<{self.user_id}>'

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/img/no_photo.png'

    NOW_PLAYING_TTL_MINUTES = 15

    @property
    def is_listening_now(self):
        if not self.now_playing_id or not self.now_playing_at:
            return False
        from datetime import timedelta
        from django.utils import timezone
        return (timezone.now() - self.now_playing_at) < timedelta(minutes=self.NOW_PLAYING_TTL_MINUTES)

    # Profile completion (own page only): list of (label, points, satisfied)
    COMPLETION_ITEMS = (
        ('Загрузить фотографию', 20, lambda p: bool(p.avatar)),
        ('Указать дату рождения', 10, lambda p: bool(p.birth_date)),
        ('Указать родной город', 10, lambda p: bool(p.home_city)),
        ('Указать образование',  5,  lambda p: bool(p.education)),
        ('Семейное положение',  5,  lambda p: bool(p.marital_status)),
        ('Полит. взгляды',      5,  lambda p: bool(p.political_views)),
        ('Заполнить «о себе»',  10, lambda p: bool(p.about)),
        ('Заполнить интересы',  10, lambda p: bool(p.interests)),
        ('Любимая музыка',      5,  lambda p: bool(p.favourite_music)),
        ('Любимые фильмы',      5,  lambda p: bool(p.favourite_movies)),
        ('Любимые книги',       5,  lambda p: bool(p.favourite_books)),
        ('Добавить контакты',   10, lambda p: bool(p.skype or p.icq or p.site or p.mobile_phone)),
    )

    def completion(self):
        """Returns dict {percent, missing: [(label, points), ...]}."""
        percent = 0
        missing = []
        for label, points, check in self.COMPLETION_ITEMS:
            if check(self):
                percent += points
            else:
                missing.append((label, points))
        return {'percent': percent, 'missing': missing}

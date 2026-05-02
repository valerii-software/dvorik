import io
import random
from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from friends.models import Friendship
from groups.models import Group, GroupMember
from messaging.models import Dialog, Message
from photos.models import Album, Photo, PhotoTag
from wall.models import WallPost


def make_demo_image(text, color):
    img = Image.new('RGB', (600, 400), color)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 599, 399), outline='#FFFFFF', width=2)
    d.text((20, 20), text, fill='#FFFFFF')
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=82)
    return ContentFile(buf.getvalue())

User = get_user_model()

DEMO = [
    ('Павел', 'Дуров', 'pavel@vk.local', 'Санкт-Петербург', 'СПбГУ, филфак.', 'Программирование, восточные единоборства, чтение.'),
    ('Анна', 'Иванова', 'anna@vk.local', 'Москва', 'МГУ, журфак, 3 курс.', 'Музыка, путешествия, фотография.'),
    ('Михаил', 'Петров', 'mikhail@vk.local', 'Новосибирск', 'НГУ, физфак.', 'Футбол, кино, программирование.'),
    ('Екатерина', 'Смирнова', 'katya@vk.local', 'Казань', 'КФУ, экономика.', 'Книги, йога, рисование.'),
    ('Дмитрий', 'Кузнецов', 'dmitry@vk.local', 'Екатеринбург', 'УрФУ, ИРИТ-РТФ.', 'Игры, аниме, гитара.'),
    ('Ольга', 'Соколова', 'olga@vk.local', 'Нижний Новгород', 'ННГУ, биофак.', 'Природа, велосипед, кулинария.'),
]


class Command(BaseCommand):
    help = 'Seeds demo users, friendships, wall posts, and messages.'

    def handle(self, *args, **opts):
        users = []
        for first, last, email, city, activity, interests in DEMO:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': first,
                    'last_name': last,
                },
            )
            if created:
                user.set_password('demo1234')
                user.save()
            p = user.profile
            p.home_city = city
            p.activity = activity
            p.interests = interests
            p.gender = 'm' if first in ('Павел', 'Михаил', 'Дмитрий') else 'f'
            p.birth_date = date(1985 + random.randint(0, 15), random.randint(1, 12), random.randint(1, 28))
            p.about = f'Привет! Я {first}.'
            p.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f'Users: {len(users)} (password: demo1234)'))

        # friendships: pavel <-> all
        pavel = users[0]
        for u in users[1:]:
            if not Friendship.objects.filter(from_user=pavel, to_user=u).exists() and \
               not Friendship.objects.filter(from_user=u, to_user=pavel).exists():
                Friendship.objects.create(
                    from_user=pavel, to_user=u, status=Friendship.ACCEPTED,
                )
        # one pending request to pavel
        if not Friendship.objects.filter(from_user=users[3], to_user=users[1]).exists():
            Friendship.objects.create(from_user=users[3], to_user=users[1], status=Friendship.PENDING)

        # wall posts
        if not WallPost.objects.exists():
            WallPost.objects.create(owner=pavel, author=users[1], text='С днём рождения, Паша!')
            WallPost.objects.create(owner=pavel, author=users[2], text='Привет! Спасибо за то, что делаешь.')
            WallPost.objects.create(owner=users[1], author=pavel, text='Анна, привет! Как дела?')

        # one dialog with messages
        d = Dialog.get_or_create_between(pavel, users[1])
        if not d.messages.exists():
            Message.objects.create(dialog=d, sender=users[1], text='Привет, Паша!')
            Message.objects.create(dialog=d, sender=pavel, text='Привет, Анна! Как ты?')
            Message.objects.create(dialog=d, sender=users[1], text='Отлично, спасибо! :)')

        # groups
        if not Group.objects.exists():
            club = Group.objects.create(
                owner=pavel, name='Клуб любителей пельменей',
                description='Здесь обсуждаем сорта пельменей, рецепты и места.',
            )
            for u in [pavel, users[1], users[2], users[4]]:
                GroupMember.objects.get_or_create(group=club, user=u)
            WallPost.objects.create(
                group=club, author=pavel,
                text='Всем привет! Записывайтесь и делитесь рецептами.',
            )
            WallPost.objects.create(
                group=club, author=users[2],
                text='Сегодня сделал пельмени с грибами — рекомендую!',
            )

            second = Group.objects.create(
                owner=users[1], name='МГУ — журфак',
                description='Сообщество студентов и выпускников.',
            )
            for u in [users[1], users[3]]:
                GroupMember.objects.get_or_create(group=second, user=u)
            WallPost.objects.create(
                group=second, author=users[1],
                text='Кто пойдёт на лекцию в субботу?',
            )

        # photo albums
        if not Album.objects.exists():
            palettes = [
                ('Лето 2010', '#5BA0E0', ['Море', 'Пляж', 'Закат', 'Друзья']),
                ('С друзьями', '#7FB36A', ['Вечеринка', 'Парк', 'Кафе']),
            ]
            for owner, (title, color, captions) in zip([pavel, users[1]], palettes):
                album = Album.objects.create(owner=owner, title=title, description=f'Альбом «{title}».')
                first = None
                for cap in captions:
                    p = Photo(album=album, uploader=owner, description=cap)
                    p.image.save(f'{title}_{cap}.jpg', make_demo_image(f'{title} — {cap}', color), save=False)
                    p.save()
                    first = first or p
                if first:
                    album.cover = first
                    album.save(update_fields=['cover'])
                # tag a friend on the first photo
                if first and owner == pavel:
                    PhotoTag.objects.get_or_create(
                        photo=first, user=users[1],
                        defaults={'created_by': pavel},
                    )

        self.stdout.write(self.style.SUCCESS('Demo data ready.'))

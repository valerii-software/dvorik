import random
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from friends.models import Friendship
from messaging.models import Dialog, Message
from wall.models import WallPost

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

        self.stdout.write(self.style.SUCCESS('Demo data ready.'))

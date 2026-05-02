# Дворик

Социальная сеть с интерфейсом и атмосферой 2010 года на современном стеке.
Вдохновлено «эпохой стены» (до октября 2010), сделано не как клон, а как
самостоятельный проект с собственным брендом.

**Стек:** Django 5 · Templates · HTMX · PostgreSQL (или SQLite для локалки) · Pillow.

## Возможности

- Аутентификация (email + пароль, кастомная `User` модель)
- Профиль: аватар, дата рождения, семейное положение, родной город, образование,
  политические/религиозные взгляды, Skype/ICQ, любимая музыка/фильмы/ТВ/игры/книги
  /цитаты, шкала заполненности
- Друзья: заявки, поиск с пагинацией, case-insensitive по кириллице, индикатор онлайн
- Фото: альбомы, мульти-загрузка, отметки друзей, комментарии
- Аудио: загрузка, поиск, личная коллекция, ретро-плеер в шапке (играет при навигации)
- Видео: загрузка с превью, перемотка через HTTP Range
- Стена: текстовые посты, комментарии, граффити (canvas в модалке)
- Группы: создание, вступление, отдельная стена, поиск
- Лента новостей: посты друзей и групп
- Сообщения: 1-к-1 диалоги, инбокс с непрочитанными
- 8 настроек приватности: профиль / стена / фото / аудио / видео / группы / сообщения

## Запуск

```bash
python3 -m venv .venv
.venv/bin/pip install 'Django>=5.0,<6' 'psycopg[binary]' python-dotenv Pillow dj-database-url

# по умолчанию SQLite; для Postgres — поднимите docker-compose и задайте DATABASE_URL
# docker compose up -d
# echo 'DATABASE_URL=postgres://dvorik:dvorik@localhost:5432/dvorik' > .env

.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py runserver
```

Откройте http://127.0.0.1:8000 → войдите как `pavel@dvorik.local` / `demo1234`.

Демо-пользователи: `pavel@dvorik.local`, `anna@dvorik.local`, `mikhail@dvorik.local`,
`katya@dvorik.local`, `dmitry@dvorik.local`, `olga@dvorik.local` — все с паролем `demo1234`.

## Структура

```
dvorik/      — Django-проект (settings, urls, range-aware media serve, Cyrillic LOWER)
accounts/    — кастомный User
profiles/    — Profile (поля 2010-эпохи), приватность, last_seen middleware
friends/     — Friendship, заявки, поиск
wall/        — WallPost, граффити, generic-target (user или group)
messaging/   — Dialog, Message
photos/      — Album, Photo, PhotoTag, PhotoComment
audio/       — AudioTrack + UserAudio
video/       — Video с превью
groups/      — Group + GroupMember
feed/        — лента новостей
templates/   — Django-шаблоны, base.html с шапкой, сайдбаром, плеером, модалкой
static/css/dvorik.css — Tahoma 11px, Kashmir Blue #45668E, фиксированная ширина 800px
```

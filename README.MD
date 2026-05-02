# ВКонтакте 2010 (Django)

Реплика интерфейса и базового функционала ВКонтакте «эпохи стены» (до октября 2010) на современном стеке.

**Стек:** Django 5 · Templates · HTMX · PostgreSQL (или SQLite для локалки) · Pillow.

## MVP

- Регистрация / вход / выход (email + пароль, кастомная `User` модель)
- Профиль: аватар, день рождения, семейное положение, родной город, интересы, любимая музыка/фильмы/книги/цитаты, Skype/ICQ
- Друзья: заявки (входящие/исходящие/принятие/отклонение/отмена/удаление), список друзей, поиск людей по имени и городу
- Стена: запись, комментарии, удаление (HTMX, без перезагрузки)
- Сообщения: диалоги «сверху вниз», отправка по HTMX, отметка прочитанных

## Запуск

```bash
python3 -m venv .venv
.venv/bin/pip install 'Django>=5.0,<6' 'psycopg[binary]' python-dotenv Pillow dj-database-url

# по умолчанию использует SQLite; для Postgres — поднимите docker-compose и задайте DATABASE_URL
# docker compose up -d
# echo 'DATABASE_URL=postgres://vk:vk@localhost:5432/vk2010' > .env

.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py runserver
```

Откройте http://127.0.0.1:8000 → войдите как `pavel@vk.local` / `demo1234`.

Демо-пользователи: `pavel@vk.local`, `anna@vk.local`, `mikhail@vk.local`,
`katya@vk.local`, `dmitry@vk.local`, `olga@vk.local` — все с паролем `demo1234`.

## Структура

```
accounts/    — кастомный User, регистрация / вход / выход
profiles/    — Profile (поля 2010-эпохи), просмотр и редактирование
friends/     — Friendship, заявки, поиск людей
wall/        — WallPost, WallComment, HTMX-формы
messaging/   — Dialog, Message, инбокс и переписка
templates/   — Django-шаблоны, base.html с шапкой, сайдбаром, футером
static/css/vk2010.css — стили: Tahoma 11px, Kashmir Blue #45668E, белый фон
```

## Дальше по плану (итерации)

- Этап 5 — фотоальбомы, видео/аудио
- Этап 6 — группы, лента новостей друзей
- Этап 7 — настройки приватности
- Граффити на стене

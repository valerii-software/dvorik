# Дворик

Социальная сеть с интерфейсом и атмосферой 2010 года на современном стеке.
Вдохновлено «эпохой стены» (до октября 2010), сделано не как клон, а как
самостоятельный проект с собственным брендом.

🔗 <https://github.com/valerii-software/dvorik>

**Стек:** Django 5 · Templates · HTMX · PostgreSQL (или SQLite для локалки) ·
Pillow · gunicorn · nginx.

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

## Локальная разработка

```bash
git clone https://github.com/valerii-software/dvorik.git
cd dvorik
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py runserver
```

Откройте <http://127.0.0.1:8000> и войдите как `pavel@dvorik.local` / `demo1234`.

Демо-пользователи: `pavel@dvorik.local`, `anna@dvorik.local`, `mikhail@dvorik.local`,
`katya@dvorik.local`, `dmitry@dvorik.local`, `olga@dvorik.local` (пароль `demo1234`).

По умолчанию используется SQLite. Чтобы поднять Postgres локально:

```bash
docker compose up -d db
echo 'DATABASE_URL=postgres://dvorik:dvorik@localhost:5432/dvorik' >> .env
```

## Деплой через docker-compose + nginx

Стек: `nginx` (порт 80) → `web` (gunicorn:8000) → `db` (postgres:16).
Статика и медиа отдаются nginx напрямую — `/static/` с длинным кэшем,
`/media/` с поддержкой HTTP Range для перемотки видео и аудио.

1. **Подготовьте `.env`** в корне проекта (см. `.env.example`):

   ```env
   SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
   DEBUG=0
   ALLOWED_HOSTS=dvorik.example.com,localhost
   CSRF_TRUSTED_ORIGINS=https://dvorik.example.com
   POSTGRES_USER=dvorik
   POSTGRES_PASSWORD=<сильный пароль>
   POSTGRES_DB=dvorik
   HTTP_PORT=80
   ```

2. **Запустите:**

   ```bash
   docker compose up -d --build
   ```

   `web` сам прогонит `collectstatic` и `migrate` при старте.

3. **(Опционально) Засейдите демо-данные:**

   ```bash
   docker compose exec web python manage.py seed_demo
   docker compose exec web python manage.py createsuperuser
   ```

4. **Логи / перезапуск:**

   ```bash
   docker compose logs -f web nginx
   docker compose restart web
   ```

### HTTPS

`nginx.conf` слушает только 80. Для боевого HTTPS вынесите TLS-терминацию
на внешний прокси (Caddy / Traefik / Cloudflare Tunnel) или допишите
`server { listen 443 ssl; … }` в `nginx.conf` и смонтируйте сертификаты.
Django уже настроен трастить `X-Forwarded-Proto`, ставить `Secure`-куки и
HSTS при `DEBUG=0`.

### Бэкап

```bash
docker compose exec db pg_dump -U dvorik dvorik > backup.sql
docker compose run --rm -v $(pwd):/backup web tar czf /backup/media.tgz media/
```

## Структура

```
dvorik/      — Django-проект (settings, urls, range-aware media serve, Cyrillic LOWER)
accounts/    — кастомный User
profiles/    — Profile, приватность, last_seen middleware
friends/     — Friendship, заявки, поиск
wall/        — WallPost, граффити, generic-target (user или group)
messaging/   — Dialog, Message
photos/      — Album, Photo, PhotoTag, PhotoComment
audio/       — AudioTrack + UserAudio
video/       — Video с превью
groups/      — Group + GroupMember
feed/        — лента новостей
templates/   — Django-шаблоны, base.html с шапкой, сайдбаром, плеером, модалкой
static/      — CSS / JS / placeholder-картинки
Dockerfile, docker-compose.yml, nginx.conf — production-стек
```

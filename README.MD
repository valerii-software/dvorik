# Дворик

> Социальная сеть в стилистике 2010 года на современном стеке.
> Не клон — самостоятельный проект с собственным брендом, вдохновлённый
> «эпохой стены» (до октября 2010).

**🌐 Живая версия — [dvorik.site](https://dvorik.site)**

[![Stack](https://img.shields.io/badge/Django-5-092E20?logo=django)](https://www.djangoproject.com/)
[![Stack](https://img.shields.io/badge/HTMX-1.9-3D72D7?logo=htmx)](https://htmx.org/)
[![Stack](https://img.shields.io/badge/Postgres-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Stack](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Stack](https://img.shields.io/badge/nginx-alpine-009639?logo=nginx&logoColor=white)](https://nginx.org/)

---

## Зачем это всё

Был такой период, примерно с 2008-го по осень 2010-го, когда соцсеть была
не лентой и не алгоритмом, а маленьким двориком, куда заходишь после
школы или пары, чтобы посмотреть, кто оставил тебе сообщение на стене,
кто нарисовал каракули в граффити, кто залил в аудиозаписи свежий альбом
Гуфа, и не появилась ли у кого-то наконец-то новая аватарка.

Никаких рекомендаций. Никакой бесконечной прокрутки. Стена — это правда
стена: пришёл, прочитал, что друзья за день написали, ответил,
закрыл вкладку. Музыка — это правда музыка: загрузил mp3, добавил в
плейлист, слушаешь весь вечер, пока делаешь домашку. Граффити — это
правда холст с восемью цветами и четырьмя кистями, в котором ты тщательно
выводишь надпись «с ДР!!!» другу, который зайдёт и увидит её на своей
стене утром.

«Дворик» — про это. Пришлось порыться в web архиве, чтобы вспомнить как выглядел тот самый ВК.
Заходите, оставьте мне сообщение на стене :*

---

## Скриншоты

### Профиль и сообщения

| Страница пользователя | Мои сообщения |
| --- | --- |
| ![Профиль](docs/screenshots/profile.png) | ![Сообщения](docs/screenshots/messages.png) |

Слева — собственная страница: аватар, статус «сейчас слушает» в шапке-плеере,
основная и контактная информация, друзья / фотографии / видео в боковой
колонке, стена с формой нового поста и кнопкой «Оставить граффити».
Справа — инбокс: 1-к-1 диалоги и групповые чаты (с пометкой `[чат]` и
числом участников), превью последнего сообщения и автообновление каждые 10 секунд.

### Фото, аудио, видео

| Альбомы | Аудиозаписи |
| --- | --- |
| ![Альбомы](docs/screenshots/photos.png) | ![Аудиозаписи](docs/screenshots/audios.png) |

| Видеозаписи | Группа со стеной |
| --- | --- |
| ![Видеозаписи](docs/screenshots/videos.png) | ![Группы](docs/screenshots/groups.png) |

- **Альбомы** — обложка, счётчик фото и дата создания; внутри — мульти-загрузка,
  отметки друзей, комментарии.
- **Аудиозаписи** — личная коллекция с поиском, плей-кнопкой и удалением;
  трек продолжает играть в шапке при переходах по сайту.
- **Видеозаписи** — превью-плитки, при открытии — `<video>` с перемоткой
  через HTTP Range.
- **Группа** — отдельная стена и список участников; владелец может
  редактировать/удалять группу; на стене работают и обычные посты, и граффити.

### Граффити

| Холст | Сохранённое на стене |
| --- | --- |
| ![Холст граффити](docs/screenshots/graffiti.png) | ![Граффити на стене](docs/screenshots/graffiti_small.png) |

Граффити рисуется в модалке: палитра, четыре толщины кисти, очистка холста,
canvas сериализуется в PNG и отправляется на стену обычным `WallPost`-ом
с прикреплённой картинкой.

### Приватность

![Приватность](docs/screenshots/privacy.png)

Восемь независимых правил видимости (страница, стена, кто пишет на стену,
фото, аудио, видео, группы, кто пишет в личку) с тремя уровнями:
`все` / `только друзья` / `только я`. Запрещённые разделы отдают
вежливую заглушку, а не 404.

---

## Возможности

- **Аутентификация** — email + пароль, кастомная `User` модель.
- **Профиль** — аватар, дата рождения, семейное положение, родной город,
  образование, политические/религиозные взгляды, Skype/ICQ/сайт, любимая
  музыка/фильмы/ТВ/игры/книги/цитаты, шкала заполненности профиля.
- **Друзья** — заявки, поиск с пагинацией (case-insensitive по кириллице),
  индикатор «онлайн» и «был в сети N минут назад».
- **Фото** — альбомы, мульти-загрузка, отметки друзей, комментарии.
- **Аудио** — загрузка, поиск, личная коллекция, ретро-плеер в шапке
  (продолжает играть при навигации, prev/next, прогресс-бар, статус
  «сейчас слушает X» в профиле).
- **Видео** — загрузка с превью, перемотка через HTTP Range.
- **Стена** — текстовые посты, комментарии, граффити (canvas в модалке).
- **Группы** — создание, вступление, отдельная стена, поиск.
- **Лента новостей** — посты друзей и групп, счётчик новых постов
  с момента последнего захода.
- **Сообщения** — 1-к-1 диалоги и групповые чаты с управлением
  участниками, прикрепление картинок, пагинация (20/стр.), inbox с
  непрочитанными.
- **Уведомления** — звук на новое сообщение и заявку в друзья,
  бейджи `(N)` в сайдбаре и в `<title>` вкладки, опрос каждые 10 секунд.
- **Приватность** — 8 настраиваемых аудиторий (всё / только друзья /
  только я) для профиля, стены, фото, аудио, видео, групп, сообщений.

---

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

Откройте <http://127.0.0.1:8000>, войдите как `pavel@dvorik.local` / `demo1234`.

По умолчанию — SQLite и in-memory кэш. Для Postgres + Redis локально:

```bash
docker compose up -d db redis
cat >> .env <<EOF
DATABASE_URL=postgres://dvorik:dvorik@localhost:5432/dvorik
REDIS_URL=redis://localhost:6379/0
EOF
```

---

## Production-стек

```
[Internet] → nginx :80 → gunicorn web:8000 → postgres db:5432
                ↓                          → redis:6379  (cache + sessions)
              /static/ (volume)
              /media/  (volume, Range-aware)
```

Что внутри:

- **nginx** — gzip, per-IP rate limit (5/мин на `/accounts/login|register/`,
  2/с на write-эндпоинты, 20/с на остальное), 30-дневный кэш `/static/`,
  HTTP Range на `/media/`, security headers.
- **gunicorn** — `gthread` воркеры, `4 workers × 4 threads`
  (env-настраиваемо), `--max-requests 1000` для защиты от утечек,
  `--worker-tmp-dir /dev/shm`.
- **redis** — кэш Django + `cached_db` сессии, `maxmemory 256mb` с
  `allkeys-lru`.
- **postgres** — `conn_max_age=600`, `conn_health_checks=True`.
- **healthchecks** — `/healthz/` пингует БД, docker-compose ждёт
  готовности DB+Redis перед стартом web.
- **Sentry** (опционально, через `SENTRY_DSN`).
- **SMTP** (опционально, через `EMAIL_HOST/USER/PASSWORD`).

### Запуск

```bash
cp .env.example .env
# отредактируйте: SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, POSTGRES_PASSWORD
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

`web` сам прогонит `collectstatic` и `migrate` при старте.

### HTTPS

`nginx.conf` слушает только 80. Production-настройки требуют HTTPS:
браузер не примет `Secure`-куки на `http://`, поэтому login и POST-формы
вернут 403. Если нужно временно подёргать сайт по голому HTTP (например,
по IP пока DNS/TLS не готов) — поставь в `.env`:

```env
INSECURE_HTTP=1
CSRF_TRUSTED_ORIGINS=http://1.2.3.4
```

Это снимет `Secure`-флаги c кук и HSTS. **Обязательно вернуть
`INSECURE_HTTP=0` после поднятия HTTPS.**

Для прода:

- Поставить перед нашим nginx ещё один прокси с TLS
  (Caddy / Traefik / Cloudflare Tunnel) — самый простой путь,
  бесплатные сертификаты.
- Или дописать `server { listen 443 ssl; … }` в [nginx.conf](nginx.conf)
  и смонтировать сертификаты от Let's Encrypt.

Django уже трастит `X-Forwarded-Proto`, ставит `Secure`-куки и HSTS
при `DEBUG=0`.

### Бэкапы

[scripts/backup.sh](scripts/backup.sh) делает gzip-дамп Postgres
и tar медиа-папки. В cron:

```cron
0 3 * * *  cd /opt/dvorik && ./scripts/backup.sh >> /var/log/dvorik-backup.log 2>&1
```

Хранит последние 14 дней, удаляет старее.

---

## Масштабирование до ~100 000 пользователей

Реалистичная нагрузка на 100k registered:

- DAU ≈ 10–15k, peak concurrent ≈ 1–2k, peak RPS ≈ 200–500.
- Медиа: 200–800 ГБ суммарно (фото + аудио + видео).

Текущая конфигурация **держит это на одном сервере** при условии:

| Что | Значение |
| --- | --- |
| Web | gunicorn 4w×4t = 16 параллельных запросов на 4 vCPU |
| DB  | Postgres 16, `shared_buffers 4GB`, `effective_cache_size 12GB` |
| Cache | Redis 256 MB, LRU |
| Диск | 200 GB локально для горячих данных, остальное — S3 |
| Сеть | 1 Gbit/s исходящего |

### Что докрутить, когда упрёмся

1. **Медиа на объектное хранилище** (Hetzner Object Storage / Backblaze B2 /
   Cloudflare R2) через `django-storages[s3]`. Отдавать через CDN
   (Cloudflare даёт бесплатный egress).
2. **Postgres connection pooling** — добавить `pgbouncer` между web и db,
   режим `transaction`.
3. **Celery + Redis** для асинхронных задач (генерация thumbnail,
   отправка email). Добавится сервис `worker`.
4. **CDN перед nginx** — Cloudflare/Bunny отдадут `/static/` и `/media/`
   из edge-кэша. Снимет ~70% трафика с VPS.
5. **Read replica** Postgres для тяжёлых выборок (лента, поиск).
6. **Горизонтальное масштабирование web** — поднять второй `web`
   контейнер, nginx уже знает про upstream-балансировку.

### Где хостить (не в РФ)

| Провайдер | Локации | Конфиг для 100k | Цена |
| --- | --- | --- | --- |
| **Hetzner Cloud** ⭐ | DE / FI / US / SG | `CCX23`: 4 dedicated vCPU, 16 GB RAM, 240 GB NVMe | ~€30/мес |
| Hetzner Cloud (бюджет) | то же | `CX42`: 8 shared vCPU, 16 GB RAM, 160 GB | ~€20/мес |
| **Scaleway** | FR / NL / PL | `PLAY2-PICO` (4 vCPU, 16 GB) | ~€32/мес |
| **OVH** | EU + Canada | `B3-32`: 8 vCPU, 32 GB RAM, 100 GB | ~€60/мес |
| **DigitalOcean** | EU / US / SG | Premium AMD, 8 vCPU / 16 GB | ~$84/мес |
| **Vultr High-Frequency** | глобально | 8 vCPU / 16 GB | ~$96/мес |

**Рекомендация — Hetzner.** Лучшее соотношение цена / производительность,
EU-юрисдикция, входящий трафик бесплатный, пиринг с Cloudflare стабилен.
Минимальный production-конфиг под 100k активных:

```
Hetzner CCX23  (€30/мес)         — все контейнеры стека
Hetzner Object Storage (~€5/мес) — фото/аудио/видео
Cloudflare Free                  — CDN + TLS + WAF
                            ───────────────────
                            Итого ≈ €35/мес
```

При росте до ~500k — выносим Postgres на отдельный CCX23, поднимаем
второй web-нод за тем же nginx, переключаем медиа на R2.

---

## Структура

```
dvorik/      — Django-проект (settings, urls, range-aware dev media,
               Cyrillic LOWER, /healthz/)
accounts/    — кастомный User
profiles/    — Profile, приватность, last_seen middleware,
               news_seen_at для счётчика новостей
friends/     — Friendship, заявки, поиск
wall/        — WallPost, граффити, generic-target (user или group)
messaging/   — Dialog (M2M-участники), Message с прикреплением картинок,
               групповые чаты, пагинация
photos/      — Album, Photo, PhotoTag, PhotoComment
audio/       — AudioTrack + UserAudio, ретро-плеер в шапке
video/       — Video с превью, HTTP-Range
groups/      — Group + GroupMember
feed/        — лента новостей
templates/   — Django-шаблоны: base.html с шапкой/сайдбаром/плеером/
               модалкой; HTMX boost + опрос для нотификаций
static/      — CSS / JS / звуки уведомлений / placeholder-картинки
scripts/     — backup.sh, deploy.sh
Dockerfile, docker-compose.yml, nginx.conf, proxy.inc
```

---

## Лицензия

MIT.

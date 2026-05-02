# Дворик

Социальная сеть с интерфейсом и атмосферой 2010 года на современном стеке.
Вдохновлено «эпохой стены» (до октября 2010), сделано не как клон, а как
самостоятельный проект с собственным брендом.

🔗 <https://github.com/valerii-software/dvorik>

**Стек:** Django 5 · Templates · HTMX · PostgreSQL · Redis · gunicorn · nginx · Pillow.

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
- 8 настроек приватности

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

По умолчанию используется SQLite и in-memory кэш. Для Postgres + Redis локально:

```bash
docker compose up -d db redis
cat >> .env <<EOF
DATABASE_URL=postgres://dvorik:dvorik@localhost:5432/dvorik
REDIS_URL=redis://localhost:6379/0
EOF
```

## Production-стек (docker compose)

```
[Internet] → nginx :80 → gunicorn web:8000 → postgres db:5432
                ↓                          → redis:6379 (cache + sessions)
              /static/ (volume)
              /media/  (volume, Range-aware)
```

Что внутри:

- **nginx** — gzip, per-IP rate limit (5/мин на /accounts/login|register/, 2/с
  на write-эндпоинты, 20/с на остальное), 30-дневный кэш `/static/`,
  HTTP Range на `/media/`, security headers.
- **gunicorn** — `gthread` воркеры, 4 workers × 4 threads (env-настраиваемо),
  `--max-requests 1000` для защиты от утечек, `--worker-tmp-dir /dev/shm`.
- **redis** — кэш Django + `cached_db` сессии, `maxmemory 256mb` с
  `allkeys-lru`.
- **postgres** — `conn_max_age=600`, `conn_health_checks=True`.
- **healthchecks** — `/healthz/` пингует БД, docker-compose ждёт DB+Redis
  готовности перед стартом web.
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

Это снимет `Secure`-флаги c кук и HSTS. **Обязательно вернуть `INSECURE_HTTP=0`
после поднятия HTTPS.**

Для прода:
- Поставьте перед нашим nginx ещё один прокси с TLS (Caddy / Traefik /
  Cloudflare Tunnel) — самый простой путь, бесплатные сертификаты.
- Или допишите `server { listen 443 ssl; … }` в [nginx.conf](nginx.conf)
  и смонтируйте сертификаты от Let's Encrypt.

Django уже трастит `X-Forwarded-Proto`, ставит `Secure`-куки и HSTS
при `DEBUG=0`.

### Бэкапы

[scripts/backup.sh](scripts/backup.sh) делает gzip-дамп Postgres и tar
медиа-папки. Подключите в cron:

```cron
0 3 * * *  cd /opt/dvorik && ./scripts/backup.sh >> /var/log/dvorik-backup.log 2>&1
```

Хранит последние 14 дней, удаляет старее.

## Масштабирование до ~100 000 пользователей

Реалистичная нагрузка на 100k registered:
- DAU ≈ 10–15k, peak concurrent ≈ 1–2k, peak RPS ≈ 200–500.
- Медиа: 200–800 ГБ суммарно (фото + аудио + видео).

Текущая конфигурация **держит это на одном сервере** при условии:

| Что | Значение |
| --- | --- |
| Web | gunicorn 4w×4t = 16 параллельных запросов на 4 vCPU |
| DB  | Postgres 16, `shared_buffers 4GB`, `effective_cache_size 12GB` (тюнинг отдельно) |
| Cache | Redis 256 MB, LRU |
| Диск | 200 GB локально для горячих данных, остальное на S3-совместимое объектное хранилище |
| Сеть | 1 Gbit/s исходящего вполне хватит |

### Что докрутить, когда упрёмся

1. **Медиа на объектное хранилище** (Hetzner Object Storage / Backblaze B2 /
   Cloudflare R2) через `django-storages[s3]`. Отдавать через CDN
   (Cloudflare даёт бесплатный egress). Локальный диск перестанет быть
   bottleneck.
2. **Postgres connection pooling** — добавить контейнер `pgbouncer` между
   web и db, режим `transaction`. Особенно если будет много воркеров.
3. **Celery + Redis** для асинхронных задач (генерация thumbnail на upload,
   отправка email). Добавится сервис `worker`.
4. **CDN перед nginx** — Cloudflare/Bunny отдадут `/static/` и `/media/`
   из edge-кэша, остальное проксируют. Снимет ~70% трафика с VPS.
5. **Read replica** Postgres для тяжёлых выборок (лента, поиск).
6. **Горизонтальное масштабирование web** — поднять второй `web` контейнер,
   nginx уже знает про upstream-балансировку (`upstream django { server web:8000; }` →
   добавить `server web2:8000`).

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
Добавьте Hetzner Object Storage или Backblaze B2 (~€5 / $6 за 1 ТБ) для
медиа и Cloudflare (бесплатный план) перед сайтом — DDoS-фильтр + CDN +
TLS из коробки.

Минимальный production-конфиг под 100k активных:

```
Hetzner CCX23  (€30/мес)        — все контейнеры стека
Hetzner Object Storage (~€5/мес) — фото/аудио/видео
Cloudflare Free                 — CDN + TLS + WAF
                            ───────────────────
                            Итого ≈ €35/мес
```

При росте до ~500k активных — выносим Postgres на отдельный CCX23,
поднимаем второй web-нод за тем же nginx, переключаем медиа на R2.

## Структура

```
dvorik/      — Django-проект (settings, urls, range-aware dev media, Cyrillic LOWER, /healthz/)
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
scripts/backup.sh — cron-friendly бэкап Postgres + media
Dockerfile, docker-compose.yml, nginx.conf, proxy.inc — production-стек
```

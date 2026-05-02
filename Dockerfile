FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    GUNICORN_WORKERS=4 \
    GUNICORN_THREADS=4

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# collectstatic runs again at container start (after volume mount).
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["sh", "-c", "\
    python manage.py collectstatic --noinput && \
    python manage.py migrate --noinput && \
    exec gunicorn dvorik.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers ${GUNICORN_WORKERS:-4} \
        --threads ${GUNICORN_THREADS:-4} \
        --worker-class gthread \
        --worker-tmp-dir /dev/shm \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --timeout 60 \
        --keep-alive 5 \
        --access-logfile - --error-logfile -"]

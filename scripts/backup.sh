#!/usr/bin/env bash
# Daily backup helper. Run from the project root or via cron:
#   0 3 * * *  cd /opt/dvorik && ./scripts/backup.sh >> /var/log/dvorik-backup.log 2>&1
#
# Produces:
#   $BACKUP_DIR/db-YYYY-MM-DD.sql.gz   (full pg_dump)
#   $BACKUP_DIR/media-YYYY-MM-DD.tar   (incremental: only files newer than yesterday's archive)
#
# Keeps the last $RETENTION_DAYS days, deletes older.

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
STAMP=$(date +%F)

mkdir -p "$BACKUP_DIR"

echo "[$(date -Iseconds)] dumping postgres → $BACKUP_DIR/db-$STAMP.sql.gz"
docker compose exec -T db pg_dump -U "${POSTGRES_USER:-dvorik}" "${POSTGRES_DB:-dvorik}" \
    | gzip > "$BACKUP_DIR/db-$STAMP.sql.gz"

echo "[$(date -Iseconds)] archiving media → $BACKUP_DIR/media-$STAMP.tar"
docker compose run --rm -v "$(pwd)/$BACKUP_DIR:/backup" web \
    tar -cf "/backup/media-$STAMP.tar" -C / app/media

echo "[$(date -Iseconds)] pruning archives older than $RETENTION_DAYS days"
find "$BACKUP_DIR" -maxdepth 1 -type f \( -name 'db-*.sql.gz' -o -name 'media-*.tar' \) \
    -mtime +"$RETENTION_DAYS" -delete

echo "[$(date -Iseconds)] done"

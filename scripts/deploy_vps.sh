#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/aurion-mvp}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.vps.yml}"
BACKUP_DIR="${BACKUP_DIR:-/opt/aurion-backups}"
DB_PATH="${DB_PATH:-$APP_DIR/data/aurion.db}"

mkdir -p "$BACKUP_DIR"

if [ -f "$DB_PATH" ]; then
  ts="$(date +%Y%m%d-%H%M%S)"
  cp "$DB_PATH" "$BACKUP_DIR/aurion-$ts.db"
fi

cd "$APP_DIR"
git fetch --all --prune
git checkout main
git pull --ff-only origin main

docker compose -f "$COMPOSE_FILE" pull
docker compose -f "$COMPOSE_FILE" up -d --no-deps --build api

for i in $(seq 1 20); do
  if curl -fsS "http://127.0.0.1:8001/health" >/dev/null; then
    echo "Healthcheck passed."
    exit 0
  fi
  sleep 3
done

echo "Healthcheck failed after deploy" >&2
exit 1

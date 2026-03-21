#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/aurion-mvp}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.vps.yml}"
BACKUP_DIR="${BACKUP_DIR:-/opt/aurion-backups}"
DB_PATH="${DB_PATH:-$APP_DIR/data/aurion.db}"
HEALTHCHECK_URL="${HEALTHCHECK_URL:-http://127.0.0.1:8001/health}"
APP_UID="${APP_UID:-10001}"
APP_GID="${APP_GID:-10001}"

mkdir -p "$BACKUP_DIR"
mkdir -p "$APP_DIR/data"

# Ensure the mounted SQLite volume stays writable for the non-root container user.
chown -R "$APP_UID:$APP_GID" "$APP_DIR/data"

require_bin() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_bin git
require_bin docker
require_bin curl

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
  if curl -fsS "$HEALTHCHECK_URL" >/dev/null; then
    echo "Healthcheck passed."
    exit 0
  fi
  sleep 3
done

echo "Healthcheck failed after deploy" >&2
docker compose -f "$COMPOSE_FILE" logs --tail=120 api || true
exit 1

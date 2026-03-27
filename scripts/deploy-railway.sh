#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env.windsurf.local"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

if [[ -z "${RAILWAY_TOKEN:-}" ]]; then
  echo "RAILWAY_TOKEN is not set. Fill /Users/natalacernikova/Downloads/aurion-stage13/aurion-backend/.env.windsurf.local"
  exit 1
fi

export PATH="/tmp/aurion-node/node-v24.14.0-darwin-arm64/bin:$PATH"

cd "$ROOT_DIR"

CMD=(npx @railway/cli up)

if [[ -n "${RAILWAY_SERVICE:-}" ]]; then
  CMD+=(--service "$RAILWAY_SERVICE")
fi

if [[ -n "${RAILWAY_ENVIRONMENT:-}" ]]; then
  CMD+=(--environment "$RAILWAY_ENVIRONMENT")
fi

echo "Deploying Aurion OS to Railway..."
RAILWAY_TOKEN="$RAILWAY_TOKEN" "${CMD[@]}"

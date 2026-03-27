#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env.windsurf.local"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

if [[ -z "${VERCEL_TOKEN:-}" ]]; then
  echo "VERCEL_TOKEN is not set. Fill /Users/natalacernikova/Downloads/aurion-stage13/aurion-backend/.env.windsurf.local"
  exit 1
fi

export PATH="/tmp/aurion-node/node-v24.14.0-darwin-arm64/bin:$PATH"

cd "$ROOT_DIR"
echo "Deploying Aurion OS to Vercel production..."
npx vercel deploy --prod --token "$VERCEL_TOKEN" -y

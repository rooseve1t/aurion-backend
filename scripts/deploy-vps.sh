#!/bin/bash
# Aurion Deployment Script for VPS (62.152.55.52)
# Run this on the server after git pull

set -e

echo "🚀 Aurion OS Deployment Script"
echo "=============================="

# 1. Update code
echo "📦 Pulling latest code..."
cd /opt/aurion-mvp
git fetch --all --prune
git checkout main
git pull --ff-only origin main

# 2. Setup environment
echo "🔧 Setting up environment..."
if [ ! -f .env.vps ]; then
    echo "⚠️  .env.vps not found! Creating template..."
    cat > .env.vps << 'EOF'
ENVIRONMENT=production
POSTGRES_USER=aurion
POSTGRES_PASSWORD=CHANGE_ME
POSTGRES_DB=aurion
DATABASE_URL=postgresql+asyncpg://aurion:CHANGE_ME@postgres:5432/aurion
REDIS_URL=redis://redis:6379/0
ALLOWED_ORIGINS=https://aurionai.ru,https://www.aurionai.ru
EOF
    echo "❌ Please edit .env.vps and set POSTGRES_PASSWORD!"
    exit 1
fi

# 3. Build and restart containers
echo "🐳 Building containers..."
docker compose -f docker-compose.vps.yml down
docker compose -f docker-compose.vps.yml up -d --build

# 4. Health check
echo "🏥 Health check..."
sleep 5
curl -sS http://127.0.0.1:8001/health || echo "⚠️  Health check failed"

# 5. Show status
echo ""
echo "✅ Deployment complete!"
echo ""
docker compose -f docker-compose.vps.yml ps
echo ""
echo "Check logs: docker compose -f docker-compose.vps.yml logs -f api"

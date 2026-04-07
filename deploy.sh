#!/bin/bash
#
# 🚀 Aurion OS PWA — Deploy Script
# Запусти этот скрипт на своей машине для мгновенного деплоя
#
# Использование:
#   chmod +x deploy.sh && ./deploy.sh
#
# Или выбери конкретную платформу:
#   ./deploy.sh vercel
#   ./deploy.sh surge
#   ./deploy.sh netlify

set -e

DIST_DIR="dist"
PLATFORM="${1:-auto}"

# Цвета
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════╗"
echo "║   🤖 AURION OS — PWA Deploy          ║"
echo "║   J.A.R.V.I.S. Deployment Protocol   ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

# Проверяем что dist/ существует
if [ ! -d "$DIST_DIR" ]; then
    echo -e "${YELLOW}⚙ Собираю проект...${NC}"
    npm run build
fi

# SPA fallback
if [ ! -f "$DIST_DIR/200.html" ]; then
    cp "$DIST_DIR/index.html" "$DIST_DIR/200.html"
fi

echo -e "${GREEN}✅ dist/ готов ($(du -sh $DIST_DIR | cut -f1))${NC}"
echo ""

deploy_vercel() {
    echo -e "${CYAN}🔺 Деплой на Vercel...${NC}"
    if ! command -v vercel &>/dev/null; then
        npm i -g vercel
    fi
    vercel deploy --prod
    echo -e "${GREEN}✅ Задеплоено на Vercel!${NC}"
}

deploy_surge() {
    echo -e "${CYAN}⚡ Деплой на Surge.sh...${NC}"
    if ! command -v surge &>/dev/null; then
        npm i -g surge
    fi
    surge ./dist aurion-jarvis.surge.sh
    echo -e "${GREEN}✅ Задеплоено: https://aurion-jarvis.surge.sh${NC}"
}

deploy_netlify() {
    echo -e "${CYAN}🌐 Деплой на Netlify...${NC}"
    if ! command -v netlify &>/dev/null; then
        npm i -g netlify-cli
    fi
    netlify deploy --prod --dir=dist
    echo -e "${GREEN}✅ Задеплоено на Netlify!${NC}"
}

deploy_auto() {
    echo "Выбери платформу:"
    echo "  1) Vercel    — CDN, авто-SSL, preview deploys"
    echo "  2) Surge.sh  — мгновенный, простой"
    echo "  3) Netlify   — drag & drop, forms, functions"
    echo ""
    read -p "Номер (1-3): " choice
    case $choice in
        1) deploy_vercel ;;
        2) deploy_surge ;;
        3) deploy_netlify ;;
        *) echo -e "${RED}Неизвестный выбор${NC}"; exit 1 ;;
    esac
}

case $PLATFORM in
    vercel)  deploy_vercel ;;
    surge)   deploy_surge ;;
    netlify) deploy_netlify ;;
    auto|*)  deploy_auto ;;
esac

echo ""
echo -e "${CYAN}📱 PWA готов к установке!${NC}"
echo "   Открой URL в Chrome → ⋮ → Установить приложение"
echo ""
echo -e "${GREEN}J.A.R.V.I.S. deployment complete, sir.${NC}"

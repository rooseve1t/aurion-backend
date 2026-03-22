# 🔑 ПОЛНЫЙ СПИСОК ВСЕХ КЛЮЧЕЙ AURION OS
# 100% полный перечень всех требуемых переменных окружения

## 🗄️ БАЗА ДАННЫХ
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/aurion_os
POSTGRES_USER=aurion
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aurion_os

## 🧠 AI/LLM ПРОВАЙДЕРЫ
# OpenAI (JARVIS, Whisper, GPT-4)
OPENAI_API_KEY=sk-...

# Anthropic Claude (альтернативный LLM)
ANTHROPIC_API_KEY=sk-ant-...

## 🎤 ГОЛОСОВЫЕ СЕРВИСЫ
# ElevenLabs (премиум TTS)
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB

# Azure Speech Services (TTS/STT)
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=eastus

# Yandex Cloud (русский язык)
YANDEX_API_KEY=...
YANDEX_FOLDER_ID=...

# VOSK (оффлайн STT)
VOSK_MODEL_PATH=models/vosk-model-small-ru-0.22

## 🕵️ OSINT И РАЗВЕДКА
# Censys (поиск инфраструктуры)
CENSYS_API_ID=...
CENSYS_API_SECRET=...

# Shodan (сканирование портов)
SHODAN_API_KEY=...

# Apify (веб-скрапинг)
APIFY_API_TOKEN=...

## 🏦 ФИНАНСОВЫЕ API
# Сбербанк
SBER_CLIENT_ID=...
SBER_CLIENT_SECRET=...

# Тинькофф
TINKOFF_CLIENT_ID=...
TINKOFF_CLIENT_SECRET=...

# Альфа-Банк
ALPHA_CLIENT_ID=...
ALPHA_CLIENT_SECRET=...

## ⚛️ КВАНТОВЫЕ ВЫЧИСЛЕНИЯ
# Quantum Rings
QUANTUM_RINGS_TOKEN=...

## 🏠 УМНЫЙ DOM (MQTT)
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_USERNAME=...
MQTT_PASSWORD=...

## 🗄️ КЭШИРОВАНИЕ
REDIS_URL=redis://localhost:6379/0

## 🔐 БЕЗОПАСНОСТЬ
# JWT токены
JWT_SECRET_KEY=your_jwt_secret_32_chars_min
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Шифрование данных
ENCRYPTION_KEY=your_fernet_key_32_chars

## 🌍 НАСТРОЙКИ ОКРУЖЕНИЯ
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

## 🎯 НАСТРОЙКИ ПРОВАЙДЕРОВ ПО УМОЛЧАНИЮ
TTS_PROVIDER=elevenlabs
STT_PROVIDER=openai
LLM_PROVIDER=openai

## 📱 PWA И МОБИЛЬНЫЕ НАСТРОЙКИ
PWA_ENABLED=True
NOTIFICATION_ENABLED=True

## 🌐 СЕТЕВЫЕ НАСТРОЙКИ
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=["*"]

## 📊 МОНИТОРИНГ И ЛОГИРОВАНИЕ
SENTRY_DSN=...  # опционально
LOG_FILE=logs/aurion.log

## 🔄 НАСТРОЙКИ РАБОТЫ С БАЗОЙ
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30

## 🧪 ТЕСТИРОВАНИЕ
TEST_DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/aurion_test

## 📧 EMAIL (опционально)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
EMAIL_FROM=...

## 🌍 ГЕОЛОКАЦИЯ (опционально)
IPINFO_API_TOKEN=...

## 🎮 ДОПОЛНИТЕЛЬНЫЕ ИНТЕГРАЦИИ
# Telegram Bot
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# Discord Webhook
DISCORD_WEBHOOK_URL=...

# Slack Webhook
SLACK_WEBHOOK_URL=...

---
## 📋 ИТОГО: 45+ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ

🔥 **ОБЯЗАТЕЛЬНЫЕ МИНИМУМ ДЛЯ ЗАПУСКА:**
- DATABASE_URL
- OPENAI_API_KEY  
- REDIS_URL
- JWT_SECRET_KEY
- ENCRYPTION_KEY

🚀 **ПОЛНЫЙ ФУНКЦИОНАЛ:**
- Все голосовые провайдеры
- OSINT разведка
- Финансовые API
- Квантовые вычисления
- Умный дом
- PWA возможности

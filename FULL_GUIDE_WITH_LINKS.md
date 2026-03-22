# 🔗 ПОЛНЫЕ ССЫЛКИ И ИНСТРУКЦИИ ДЛЯ ВСЕХ КЛЮЧЕЙ AURION OS

## 🗄️ БАЗА ДАННЫХ

### PostgreSQL с pgvector через Supabase (БЕСПЛАТНО)
**🔗 Ссылка:** https://supabase.com/dashboard/project
**📋 Инструкция:**
1. Перейдите на https://supabase.com
2. Нажмите "Start your project" → "Sign up with GitHub"
3. Создайте новый проект:
   - Organization: "Aurion OS"
   - Project Name: "aurion-backend"
   - Database Password: создайте надежный пароль
   - Region: выберите ближайший (EU West)
4. Дождитесь развертывания (2-3 минуты)
5. В проекте перейдите: Settings → Database
6. Скопируйте **Connection string**
7. В **SQL Editor** выполните: `CREATE EXTENSION IF NOT EXISTS vector;`

**🎯 Что скопировать:** `DATABASE_URL=postgresql+asyncpg://postgres.ваш-пароль@aws-0-...supabase.co:5432/postgres`

---

## 🧠 AI/LLM ПРОВАЙДЕРЫ

### OpenAI (ОБЯЗАТЕЛЬНО)
**🔗 Ссылка:** https://platform.openai.com/api-keys
**📋 Инструкция:**
1. Войдите в https://platform.openai.com
2. В левом меню → "API keys"
3. Нажмите "Create new secret key"
4. Имя: "Aurion-JARVIS"
5. Скопируйте ключ (начинается с sk-)
6. **Сохраните немедленно - больше не покажет!**

**🎯 Что скопировать:** `OPENAI_API_KEY=sk-proj-...`

### Anthropic Claude (альтернатива)
**🔗 Ссылка:** https://console.anthropic.com/
**📋 Инструкция:**
1. Зарегистрируйтесь на Anthropic Console
2. Перейдите в "API Keys"
3. Создайте новый ключ
4. Скопируйте ключ (начинается с sk-ant-)

**🎯 Что скопировать:** `ANTHROPIC_API_KEY=sk-ant-...`

---

## 🎤 ГОЛОСОВЫЕ СЕРВИСЫ

### ElevenLabs (Премиум TTS - РЕКОМЕНДУЮ)
**🔗 Ссылка:** https://elevenlabs.io/app/settings/api-keys
**📋 Инструкция:**
1. Зарегистрируйтесь на ElevenLabs
2. Пополните баланс ($5+ для начала)
3. Profile → API Keys → "Create API Key"
4. Для русского языка рекомендую голос "Adam" или "Domi"
5. В Voices выберите голос и скопируйте Voice ID

**🎯 Что скопировать:** 
```
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB
```

### Azure Speech Services (бэкап вариант)
**🔗 Ссылка:** https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.CognitiveServices%2Faccounts
**📋 Инструкция:**
1. Войдите в Azure Portal
2. Создайте ресурс: "Create a resource" → "AI services" → "Speech Services"
3. Location: East US (или другой)
4. Pricing tier: Standard S0
5. После создания → "Keys and Endpoint"
6. Скопируйте Key 1 и Location

**🎯 Что скопировать:**
```
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=eastus
```

### Yandex Cloud (для русского языка)
**🔗 Ссылка:** https://cloud.yandex.ru/
**📋 Инструкция:**
1. Создайте аккаунт Yandex ID
2. В Yandex Cloud создайте платежный аккаунт
3. Создайте сервисный аккаунт:
   - Console → Service accounts → Create
   - Дайте роль "ai.editor"
4. Создайте API ключ:
   - Service account → Create API key
5. Узнайте Folder ID (в настройках облака)

**🎯 Что скопировать:**
```
YANDEX_API_KEY=AQVN...
YANDEX_FOLDER_ID=b1g...
```

---

## 🗄️ КЭШИРОВАНИЕ

### Redis Cloud (БЕСПЛАТНО)
**🔗 Ссылка:** https://redis.com/cloud/
**📋 Инструкция:**
1. Зарегистрируйтесь на Redis Cloud
2. Создайте бесплатную базу данных (Free tier)
3. Выберите регион (ближайший)
4. После создания → "Connect" → "Redis"
5. Скопируйте Connection string

**🎯 Что скопировать:** `REDIS_URL=redis://default:password@host:port`

---

## 🕵️ OSINT РАЗВЕДКА

### Censys (инфраструктура)
**🔗 Ссылка:** https://censys.io/account
**📋 Инструкция:**
1. Зарегистрируйтесь на Censys
2. Перейдите в Account → API
3. Создайте API ID и Secret
4. Бесплатный лимит: 250 запросов/месяц

**🎯 Что скопировать:**
```
CENSYS_API_ID=...
CENSYS_API_SECRET=...
```

### Shodan (сканирование портов)
**🔗 Ссылка:** https://account.shodan.io/
**📋 Инструкция:**
1. Зарегистрируйтесь на Shodan
2. Upgrade API (доступно бесплатно)
3. В My Account → API Key скопируйте ключ

**🎯 Что скопировать:** `SHODAN_API_KEY=...`

### Apify (веб-скрапинг)
**🔗 Ссылка:** https://console.apify.com/
**📋 Инструкция:**
1. Зарегистрируйтесь на Apify Console
2. Settings → Integrations → API
3. Скопируйте API token

**🎯 Что скопировать:** `APIFY_API_TOKEN=...`

---

## 🏦 ФИНАНСОВЫЕ API

### Сбербанк (требует юрлицо/ИП)
**🔗 Ссылка:** https://developer.sber.ru/
**📋 Инструкция:**
1. Зарегистрируйтесь как юридическое лицо
2. Получите доступ к Sandbox API
3. Создайте приложение
4. Получите client_id и client_secret

**🎯 Что скопировать:**
```
SBER_CLIENT_ID=...
SBER_CLIENT_SECRET=...
```

### Тинькофф (требует юрлицо/ИП)
**🔗 Ссылка:** https://www.tinkoff.ru/develop/
**📋 Инструкция:**
1. Зарегистрируйтесь в Tinkoff Business
2. Подключите API доступ
3. Получите ключи доступа

**🎯 Что скопировать:**
```
TINKOFF_CLIENT_ID=...
TINKOFF_CLIENT_SECRET=...
```

---

## ⚛️ КВАНТОВЫЕ ВЫЧИСЛЕНИЯ

### Quantum Rings (экспериментально)
**🔗 Ссылка:** https://quantumrings.com/
**📋 Инструкция:**
1. Зарегистрируйтесь на платформе
2. Подайте заявку на доступ к API
3. Получите токен доступа

**🎯 Что скопировать:** `QUANTUM_RINGS_TOKEN=...`

---

## 🏠 УМНЫЙ DOM (MQTT)

### Локальный MQTT (бесплатно)
**🔗 Docker команда:** `docker run -it -p 1883:1883 eclipse-mosquitto`
**📋 Инструкция:**
1. Установите Docker
2. Запустите Mosquitto контейнер
3. Используйте настройки по умолчанию

**🎯 Что использовать:**
```
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
```

---

## 🔐 БЕЗОПАСНОСТЬ

### JWT Secret Key
**🔗 Генерация:** Терминал
**📋 Команда:** `openssl rand -hex 32`
**🎯 Что скопировать:** `JWT_SECRET_KEY=...`

### Encryption Key
**🔗 Генерация:** Python
**📋 Команда:** `python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
**🎯 Что скопировать:** `ENCRYPTION_KEY=...`

---

## 📋 ПОРЯДОК ПОЛУЧЕНИЯ КЛЮЧЕЙ (РЕКОМЕНДУЕТСЯ)

### 🔥 ЭТАП 1: МИНИМУМ ДЛЯ ЗАПУСКА (5 минут)
1. **OpenAI API Key** - https://platform.openai.com/api-keys
2. **Supabase Database** - https://supabase.com/dashboard/project
3. **Redis Cloud** - https://redis.com/cloud/
4. **JWT Secret** - `openssl rand -hex 32`
5. **Encryption Key** - Python команда выше

### 🚀 ЭТАП 2: ГОЛОСОВЫЕ ФУНКЦИИ (10 минут)
1. **ElevenLabs** - https://elevenlabs.io/app/settings/api-keys
2. **Azure Speech** - https://portal.azure.com/
3. **Yandex Cloud** - https://cloud.yandex.ru/

### 🕵️ ЭТАП 3: РАЗВЕДКА (10 минут)
1. **Censys** - https://censys.io/account
2. **Shodan** - https://account.shodan.io/
3. **Apify** - https://console.apify.com/

### 🏦 ЭТАП 4: ФИНАНСЫ (требует юрлицо)
1. **Сбербанк** - https://developer.sber.ru/
2. **Тинькофф** - https://www.tinkoff.ru/develop/

### ⚛️ ЭТАП 5: ЭКСПЕРИМЕНТАЛЬНОЕ
1. **Quantum Rings** - https://quantumrings.com/

---

## 💡 СОВЕТЫ

- **Сохраняйте все ключи в безопасном месте** (password manager)
- **Начните с бесплатных сервисов**
- **OpenAI и ElevenLabs самые важные для JARVIS**
- **Supabase и Redis имеют бесплатные тарифы**
- **Финансовые API требуют юридической регистрации**

**🎯 Начнем с OpenAI API Key? Он самый важный для JARVIS!**

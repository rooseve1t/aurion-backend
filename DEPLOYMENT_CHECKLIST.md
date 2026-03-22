# 🔑 AURION OS DEPLOYMENT CHECKLIST
# Сбор всех необходимых ключей и данных

## 📋 ПОШАГОВЫЙ ПЛАН СБОРА ДАННЫХ

### 1️⃣ OPENAI API KEY (JARVIS Voice Assistant)
**🔗 Ссылка:** https://platform.openai.com/api-keys
**📋 Инструкция:**
1. Зайдите в OpenAI Dashboard
2. Нажмите "Create new secret key"
3. Дайте имя "Aurion-JARVIS"
4. Скопируйте ключ (начинается с sk-)
5. Сохраните в безопасном месте

**⚙️ Переменная окружения:** `OPENAI_API_KEY=sk-...`

---

### 2️⃣ ELEVENLABS API KEY (Premium TTS)
**🔗 Ссылка:** https://elevenlabs.io/app/settings/api-keys
**📋 Инструкция:**
1. Зарегистрируйтесь в ElevenLabs
2. Перейдите в Profile → API Keys
3. Нажмите "Create API Key"
4. Скопируйте ключ
5. Выберите голос (рекомендую Adam для русского)

**⚙️ Переменные окружения:**
```
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB
```

---

### 3️⃣ POSTGRESQL DATABASE (pgvector)
**🔗 Ссылка:** https://supabase.com/dashboard/project
**📋 Инструкция:**
1. Создайте новый проект в Supabase
2. В Settings → Database найдите Connection string
3. Включите pgvector extension:
   - SQL Editor → New Query
   - `CREATE EXTENSION IF NOT EXISTS vector;`

**⚙️ Переменные окружения:**
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

---

### 4️⃣ REDIS (Кэширование)
**🔗 Ссылка:** https://redis.com/cloud/
**📋 Инструкция:**
1. Создайте бесплатный аккаунт Redis Cloud
2. Создайте новую базу данных
3. Скопируйте Connection string

**⚙️ Переменная окружения:** `REDIS_URL=redis://...`

---

### 5️⃣ AZURE SPEECH SERVICES (Альтернативный TTS)
**🔗 Ссылка:** https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.CognitiveServices%2Faccounts
**📋 Инструкция:**
1. Создайте ресурс "Speech Services"
2. В Keys and Endpoint скопируйте ключ
3. Сохраните регион (например eastus)

**⚙️ Переменные окружения:**
```
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=eastus
```

---

### 6️⃣ YANDEX CLOUD (TTS для русского)
**🔗 Ссылка:** https://cloud.yandex.ru/console/app
**📋 Инструкция:**
1. Создайте сервисный аккаунт
2. Получите API Key
3. Узнайте Folder ID

**⚙️ Переменные окружения:**
```
YANDEX_API_KEY=...
YANDEX_FOLDER_ID=...
```

---

### 7️⃣ JWT SECRET KEY
**📋 Инструкция:**
Сгенерируйте случайный ключ:
```bash
openssl rand -hex 32
```

**⚙️ Переменная окружения:** `JWT_SECRET_KEY=...`

---

### 8️⃣ ENCRYPTION KEY (Финансовый модуль)
**📋 Инструкция:**
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**⚙️ Переменная окружения:** `ENCRYPTION_KEY=...`

---

## 🚀 Готовый .env файл:

```bash
# OpenAI (JARVIS)
OPENAI_API_KEY=sk-your-openai-key-here

# ElevenLabs (Premium TTS)
ELEVENLABS_API_KEY=your-elevenlabs-key
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB

# PostgreSQL с pgvector
DATABASE_URL=postgresql://postgres:password@localhost:5432/aurion_os

# Redis
REDIS_URL=redis://localhost:6379

# Azure Speech (бэкап)
AZURE_SPEECH_KEY=your-azure-key
AZURE_SPEECH_REGION=eastus

# Yandex (русский TTS)
YANDEX_API_KEY=your-yandex-key
YANDEX_FOLDER_ID=your-folder-id

# Безопасность
JWT_SECRET_KEY=your-jwt-secret-here
ENCRYPTION_KEY=your-encryption-key-here

# Настройки
DEBUG=False
ENVIRONMENT=production
```

---

## 📋 CHECKLIST DEPLOYMENT:

- [ ] OpenAI API Key
- [ ] ElevenLabs API Key  
- [ ] PostgreSQL с pgvector
- [ ] Redis
- [ ] Azure Speech Key
- [ ] Yandex API Key
- [ ] JWT Secret
- [ ] Encryption Key

---

**🎯 После сбора всех ключей - система будет полностью готова к продакшену!**

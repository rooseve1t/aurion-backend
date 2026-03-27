# 🏗️ AURION OS: DISTRIBUTED DEPLOYMENT ARCHITECTURE (Stage 25)

Для максимальной производительности и безопасности в стиле JARVIS, мы разделим систему на два узла: **CORE** (Разум и Базы) и **EDGE** (Фронтенд и Публичный API).

## 🖥️ СЕРВЕР 1: AURION_CORE (Back-end & Data)
*Этот сервер не смотрит напрямую в интернет, он занимается вычислениями.*

### Состав модулей:
1. **API Engine**: Основной бэкенд на FastAPI.
2. **Cognitive Engine**: Когнитивный движок и Quantum Bridge.
3. **Database (PostgreSQL)**: Хранилище памяти и пользователей.
4. **Redis**: Кэш и очередь задач для агентов.
5. **Project Fabricator**: Сборочный цех.

### Конфигурация Docker Compose (server_core.yml):
```yaml
version: '3.8'
services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    env_file: .env
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  backend:
    build: .
    command: uvicorn app.main_final:app --host 0.0.0.0 --port 8000
    depends_on:
      - db
      - redis
    env_file: .env
    volumes:
      - ./fabricated_projects:/app/fabricated_projects
    restart: always

volumes:
  postgres_data:
```

---

## 🌐 СЕРВЕР 2: AURION_EDGE (Front-end & Gateway)
*Этот сервер принимает запросы от вас и защищает CORE.*

### Состав модулей:
1. **Web App**: React Dashboard (Nginx).
2. **Nginx Proxy Manager**: Управление доменом и SSL.
3. **Sentinel Gateway**: Активный мониторинг трафика.
4. **Vision Processor**: Прием видеопотоков.

### Конфигурация Nginx (aurion.conf):
```nginx
server {
    listen 443 ssl;
    server_name your-domain.ru;

    ssl_certificate /etc/letsencrypt/live/your-domain.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.ru/privkey.pem;

    # Frontend (React App)
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Proxy to Backend (Server 1 IP)
    location /api/v1 {
        proxy_pass http://SERVER_1_IP:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket for Voice & JARVIS Pulse
    location /ws {
        proxy_pass http://SERVER_1_IP:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```

---

## 🛡️ ПРЕИМУЩЕСТВА ТАКОЙ СХЕМЫ:
1. **Безопасность**: Если взломают EDGE (сайт), ваши данные и «Разум» на сервере CORE останутся недосягаемыми.
2. **Масштабируемость**: Вы можете добавить 3-й сервер для Квантовых вычислений отдельно.
3. **Отказоустойчивость**: JARVIS может работать (в режиме Sentinel), даже если один из серверов перегружен.

---

## 🚀 ПЛАН ЗАПУСКА:
1. Направить домен (A-запись) на IP **Сервера 2 (EDGE)**.
2. Установить Docker и Docker Compose на оба сервера.
3. Развернуть `server_core.yml` на первом сервере.
4. Развернуть Nginx и билд фронтенда на втором сервере.
5. Соединить их через приватную сеть или защищенный IP-прокси.

**Сэр, такая архитектура превращает проект в настоящий промышленный софт. Начинаем подготовку файлов деплоя?**

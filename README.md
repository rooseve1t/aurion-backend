# Aurion OS (MVP)

Aurion OS — MVP-платформа на FastAPI + React/Vite для персонального AI-ассистента:

- авторизация (email/username), refresh-токены, 2FA;
- память, умный дом, агенты, платежи, финансы;
- голосовой WebSocket-модуль и профили голоса;
- DIY Hub, Guardian-сканер, роутинг quantum/HPC задач;
- runtime-конфиг ключей без перезапуска через `/api/v1/config/update`.

## Стек

- Backend: `FastAPI`, `sqlite3` (core), optional `redis`, optional `postgres`.
- Frontend: `React 18`, `TypeScript`, `Vite`, `Zustand`.
- Tests: `pytest`, `vitest`, `msw`.

## Быстрый старт (локально)

1. Backend dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Frontend dependencies:

```bash
npm install
```

3. Создайте env:

```bash
cp .env.example .env
```

4. Запуск backend:

```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

5. Запуск frontend:

```bash
npm run dev
```

## Проверки качества

```bash
python3 -m pytest -q
npm run test
npm run lint
python3 -m ruff check .
python3 -m mypy app tests
```

## Переменные окружения (основные)

- Frontend:
  - `VITE_API_URL`
  - `VITE_WS_URL`
- Security/Auth:
  - `AURION_SECRET_KEY`
  - `AURION_ACCESS_TOKEN_TTL_MINUTES`
  - `AURION_REFRESH_TOKEN_TTL_DAYS`
  - `AURION_2FA_CHALLENGE_TTL_MINUTES`
  - `AURION_LOGIN_RATE_LIMIT_ATTEMPTS`
  - `AURION_LOGIN_RATE_LIMIT_WINDOW_SECONDS`
  - `AURION_LOGIN_RATE_LIMIT_BLOCK_SECONDS`
- Founder/roles:
  - `AURION_FOUNDER_EMAIL`
  - `AURION_FOUNDER_USERNAME`
  - `AURION_FOUNDER_PASSWORD`
  - `AURION_CREATOR_EMAILS`
- Integrations:
  - `QUANTUM_RINGS_TOKEN`
  - `YANDEX_FOLDER_ID`, `YANDEX_API_KEY`
  - `CENSYS_API_ID`, `CENSYS_API_SECRET`, `SHODAN_API_KEY`, `APIFY_API_TOKEN`
  - `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`
  - `GOOGLE_FIT_CLIENT_ID`, `GOOGLE_FIT_CLIENT_SECRET`
  - `REPLICATE_API_TOKEN`, `HUGGINGFACE_API_TOKEN`
  - `ELEVENLABS_API_KEY`, `PLANET_API_KEY`
  - `DATABASE_URL`, `REDIS_URL`, `HPC_UNICORE_URL`, `HPC_UNICORE_USER`, `HPC_UNICORE_PASSWORD`
  - `MQTT_HOST`

## Деплой

- VPS compose: `docker-compose.vps.yml`
- Deploy script (backup DB + healthcheck): `scripts/deploy_vps.sh`
- GitHub Actions workflow: `.github/workflows/deploy.yml`

Перед продакшеном обязательно:

- сгенерировать новый `AURION_SECRET_KEY`;
- вынести все секреты в secrets менеджер (Railway/Vercel/GitHub Secrets);
- отключить дефолтные/тестовые пароли.

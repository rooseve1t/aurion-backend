# Aurion OS: Required API Keys

Aurion uses a mix of working local fallbacks and external integrations. This project must only use keys that belong to you or your company.

Do not use leaked or public third-party secrets from GitHub dumps or "free API key packs". That creates security, billing, legal, and account-ban risks.

## Keys used by the current codebase

- `QUANTUM_RINGS_TOKEN`
  - Used in: `app/services/quantum_service.py`, `app/main.py`
  - Purpose: Quantum Rings / IonQ access

- `YANDEX_API_KEY`
- `YANDEX_FOLDER_ID`
  - Used in: `app/services/voice_jarvis_service.py`, `app/services/voice_jarvis_standalone.py`, `app/main.py`
  - Purpose: SpeechKit / Yandex voice features

- `CENSYS_API_ID`
- `CENSYS_API_SECRET`
- `SHODAN_API_KEY`
- `APIFY_API_TOKEN`
  - Used in: `app/services/osint_service.py`, `app/main.py`
  - Purpose: OSINT providers

- `YOOKASSA_SHOP_ID`
- `YOOKASSA_SECRET_KEY`
  - Used in: `app/main.py`
  - Purpose: Payments / subscriptions

- `GOOGLE_FIT_CLIENT_ID`
- `GOOGLE_FIT_CLIENT_SECRET`
  - Used in: `app/main.py`
  - Purpose: Health / wearable integrations

- `REPLICATE_API_TOKEN`
- `HUGGINGFACE_API_TOKEN`
  - Used in: `app/main.py`
  - Purpose: Creative generation / music / image workflows

- `ELEVENLABS_API_KEY`
  - Used in: `app/services/voice_jarvis_service.py`, `app/services/voice_jarvis_standalone.py`, `app/main.py`
  - Purpose: Voice generation

- `PLANET_API_KEY`
  - Used in: `app/main.py`
  - Purpose: Satellite / geo integrations

- `REDIS_URL`
  - Used in: `app/auth.py`, `app/services/osint_service.py`, `app/services/voice_jarvis_service.py`, `app/services/voice_service.py`, `app/services/quantum_service.py`, `app/services/finance_service.py`, `app/services/agent_service.py`, `app/services/smarthome_service.py`, `app/main.py`
  - Purpose: cache / queues / token state

- `DATABASE_URL`
  - Used in: `app/database.py`, `app/database_final.py`, `app/main.py`
  - Purpose: PostgreSQL connection

- `HPC_UNICORE_URL`
- `HPC_UNICORE_USER`
- `HPC_UNICORE_PASSWORD`
  - Used in: `app/main.py`
  - Purpose: HPC adapter routing

## Safe next step

Use your own keys and inject them through:

- `.env.production`
- Vercel project environment variables
- Railway environment variables
- runtime config update endpoint in `app/main.py`

## What still has local fallbacks or mocks

- Quantum extra adapters: IBM / Pasqal / Alibaba
- Health connections: mock connect flows
- Some payment / finance API branches
- Some voice and OSINT branches still include TODO or fallback responses

## Suggested rollout order

1. `REDIS_URL`, `DATABASE_URL`
2. `YANDEX_API_KEY`, `YANDEX_FOLDER_ID`
3. `YOOKASSA_*`
4. `CENSYS_*`, `SHODAN_API_KEY`, `APIFY_API_TOKEN`
5. `GOOGLE_FIT_*`
6. `REPLICATE_API_TOKEN`, `HUGGINGFACE_API_TOKEN`
7. `QUANTUM_RINGS_TOKEN`, `HPC_UNICORE_*`

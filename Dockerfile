FROM python:3.11-slim as backend

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl nodejs npm \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY package*.json ./
RUN npm ci --only=production

COPY src/ ./src/
COPY public/ ./public/
COPY index.html ./
COPY vite.config.ts ./
COPY tsconfig*.json ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "npm run build && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

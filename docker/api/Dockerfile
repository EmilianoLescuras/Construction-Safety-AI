# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# libpq for psycopg2-binary on slim; curl for healthcheck.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq5 curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements-backend.txt ./
RUN pip install -r requirements-backend.txt

COPY src ./src
COPY scripts ./scripts
COPY alembic ./alembic
COPY alembic.ini ./
COPY config ./config

RUN useradd --create-home --shell /bin/bash app \
 && mkdir -p outputs \
 && chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --retries=10 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.backend.app:app --host 0.0.0.0 --port 8000"]

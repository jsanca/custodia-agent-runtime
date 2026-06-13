# Custodia Server

Python backend for Custodia — a guarded AI operations layer for mental health administration.

All current repositories, LLM adapters, and auth are **fake/in-memory only**. Do not use real PHI in local development.

## Setup

```bash
uv sync
```

## Running checks

```bash
uv run pytest               # tests
uv run ruff check .         # lint
uv run mypy .               # type check
```

Root shortcut (runs all three):

```bash
make server-check
```

## Dev server

```bash
uv run fastapi dev src/custodia/app/main.py
```

Available endpoints in Phase 0:

```
GET /health   →  { "status": "ok", "service": "custodia-server" }
```

## Infrastructure

```bash
# From repo root — starts Postgres, Keycloak, Jaeger
docker compose up -d
```

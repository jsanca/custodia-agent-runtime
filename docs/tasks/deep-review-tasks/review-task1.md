# Review Task: Deep Review — Phase 0 Custodia Foundation

## Context

Clio implemented **Phase 0** for Custodia.

Custodia is a guarded AI operations layer for mental health administration.

Phase 0 scope:

* root folders:

  * `docs/`
  * `client/`
  * `server/`
* Python backend skeleton under `server/`
* FastAPI health endpoint
* explicit `runtime.py`
* Docker Compose foundation:

  * Postgres
  * Keycloak
  * Jaeger
  * Server
* minimal tests
* no business logic yet

Read before reviewing:

```text
README.md
AGENTS.md
```

---

## Goal

Review whether the Phase 0 implementation is a clean, idiomatic, maintainable foundation for the next phases.

This is not a feature review. This is an architectural and project hygiene review.

---

## Review Checklist

### 1. Repository Layout

Verify that the root layout is coherent:

```text
docs/
client/
server/
README.md
AGENTS.md
docker-compose.yml
```

Verify that the server layout follows the intended structure:

```text
server/
  pyproject.toml
  README.md
  Dockerfile
  .dockerignore
  .env.example
  src/custodia/
  tests/
```

Check that package folders contain `__init__.py` where needed.

---

### 2. Python Project Hygiene

Verify:

* Python 3.12+ is configured.
* `pyproject.toml` is clean.
* Dependencies are minimal.
* Runtime dependencies do not include future-phase libraries.
* Dev dependencies include pytest, ruff, mypy.
* No unnecessary framework or AI dependencies were added.

Allowed now:

```text
fastapi
pydantic
pydantic-settings
uvicorn
pytest
httpx
ruff
mypy
```

Should not be present yet:

```text
LangChain
LangGraph
OpenAI SDK
Anthropic SDK
SQLAlchemy
Alembic
OpenTelemetry SDK
MCP SDK
Redis
Celery
pgvector
```

---

### 3. Architecture Boundaries

Verify:

* `domain` does not import FastAPI, DB, LLM, Keycloak, MCP, infrastructure, or framework code.
* `application` does not depend on FastAPI or concrete infrastructure.
* `interfaces/api` owns FastAPI route definitions.
* `infrastructure` is currently mostly empty or contains only harmless placeholders/fakes.
* `app/runtime.py` is the explicit composition root.
* Route handlers are thin.
* No business logic has been placed in `main.py`.

---

### 4. Runtime Composition

Verify:

* `Runtime` exists.
* `build_runtime()` exists.
* The health endpoint uses runtime/configuration cleanly.
* No dependency injection framework was introduced.
* No global mutable service registry was introduced.
* Runtime composition is boring and explicit.

---

### 5. FastAPI Health Endpoint

Verify:

```text
GET /health
```

returns:

```json
{
  "status": "ok",
  "service": "custodia-server"
}
```

Check that route definitions are not over-engineered.

---

### 6. Settings

Verify:

* `settings.py` uses `pydantic-settings`.
* Settings include local environment values for:

  * environment
  * service name
  * database URL
  * Keycloak realm/base URL/client ID
  * Jaeger endpoint
* `.env.example` exists.
* No real secrets are committed.
* Settings are not read randomly across the codebase.

---

### 7. Docker Compose

Verify that `docker-compose.yml` includes:

* `postgres`
* `keycloak`
* `jaeger`
* `server`

Check:

* Postgres has a named volume.
* Postgres local credentials are development-only.
* Keycloak imports or references the Custodia realm.
* Jaeger UI is exposed on `16686`.
* Server exposes `8000`.
* Server has a healthcheck if practical.
* Service names match `.env.example`.

Check if `docker compose up --build` should work.

---

### 8. Keycloak Realm

Verify the realm file exists:

```text
docker/keycloak/realm/custodia-realm.json
```

Check that it includes:

* realm `custodia`
* clients:

  * `custodia-server`
  * `custodia-client`
* roles:

  * `admin`
  * `operations_manager`
  * `intake_coordinator`
  * `billing_staff`
  * `clinician`
  * `auditor`

Local test user is optional but useful.

No production secrets.

---

### 9. Tests

Verify:

* At least one unit test exists.
* Tests pass.
* Runtime test checks `build_runtime()`.
* Optional health endpoint test is clean.
* No browser/E2E tests were added.
* No test requires external LLMs or network calls.

Recommended commands:

```bash
cd server
uv sync
uv run pytest
uv run ruff check .
uv run mypy .
```

---

### 10. Security / PHI Hygiene

Verify:

* No PHI sample data.
* No clinical logic.
* No real credentials.
* No secrets in Docker files.
* No logging of sensitive data.
* No prompts or LLM code yet.

---

### 11. Over-Engineering Check

Flag if Clio added:

* unnecessary abstractions,
* generic repositories,
* fake business services,
* premature database tables,
* premature auth validation,
* LangChain/LangGraph,
* OpenTelemetry instrumentation beyond placeholders,
* multiple backend services,
* a gateway,
* MinIO,
* Redis,
* workers,
* MCP implementation,
* frontend implementation.

Phase 0 should stay boring.

---

## Expected Review Output

Produce a concise review with:

```text
PASS / WARN / FAIL
```

For each section:

1. Repository Layout
2. Python Project Hygiene
3. Architecture Boundaries
4. Runtime Composition
5. FastAPI Health Endpoint
6. Settings
7. Docker Compose
8. Keycloak Realm
9. Tests
10. Security / PHI Hygiene
11. Over-Engineering

For every WARN or FAIL, include:

* file path,
* issue,
* why it matters,
* recommended fix.

End with:

```text
Overall Verdict:
- PASS: ready for Phase 1
- WARN: fix small issues before Phase 1
- FAIL: do not proceed to Phase 1
```

---

## Important

Do not implement new features during review.

This review is only to decide whether Phase 0 is clean enough to proceed.

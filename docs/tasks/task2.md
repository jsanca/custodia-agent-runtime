# Task: Phase 0 — Initialize Custodia Server and Local Infrastructure

## Context

We are building **Custodia**.

Repository:

```text
custodia-agent-runtime
```

Product tagline:

```text
Custodia
A guarded AI operations layer for mental health administration.
```

Custodia is a Python-based agent runtime for administrative automation in behavioral health organizations. It follows a **hexagonal-inspired, Go-like Python architecture**:

* small Python protocols,
* explicit runtime composition,
* domain/application separated from infrastructure,
* FastAPI only at the boundary,
* deterministic workflows first,
* AI-assisted steps only where useful,
* auditability and observability from the beginning.

Read these files before implementing:

```text
README.md
AGENTS.md
```

This is **Phase 0** only. Do not implement the Intake Agent yet.

---

## Goal

Create the initial repository foundation:

```text
docs/
client/
server/
```

Then initialize the Python backend under:

```text
server/
```

and add a local Docker Compose foundation with:

```text
postgres
keycloak
jaeger
server
```

The purpose is to establish a clean project skeleton and local development environment.

---

## Top-Level Repository Layout

Create or preserve this root layout:

```text
docs/
client/
server/
README.md
AGENTS.md
docker-compose.yml
```

For now:

* `docs/` can contain placeholder architecture/decision folders.
* `client/` can remain empty or contain a placeholder README.
* `server/` must contain the Python backend project.

---

## Server Project Layout

Create this structure:

```text
server/
  pyproject.toml
  README.md
  Dockerfile
  .dockerignore
  .env.example

  src/
    custodia/
      __init__.py

      app/
        __init__.py
        main.py
        runtime.py
        settings.py

      domain/
        __init__.py
        identity.py
        patients.py
        intake.py
        tasks.py
        audit.py
        agents.py

      application/
        __init__.py
        ports.py
        intake_agent.py
        policy_agent.py
        daily_briefing.py
        guardrails.py

      infrastructure/
        __init__.py

        identity/
          __init__.py
          fake_auth.py

        persistence/
          __init__.py

        rag/
          __init__.py

        llm/
          __init__.py
          fake_llm.py

        observability/
          __init__.py

      interfaces/
        __init__.py

        api/
          __init__.py
          routes.py
          middleware.py

        jobs/
          __init__.py

        mcp/
          __init__.py

  tests/
    unit/
      test_runtime.py
    integration/
    evals/
```

---

## Python Tooling

Use a modern Python setup.

Prefer:

```text
uv
Python 3.12+
```

Configure `server/pyproject.toml` with:

Runtime dependencies:

```text
fastapi
pydantic
pydantic-settings
uvicorn
```

Development dependencies:

```text
pytest
httpx
ruff
mypy
```

Do not add these yet:

```text
LangChain
LangGraph
OpenAI SDK
Anthropic SDK
SQLAlchemy
Alembic
OpenTelemetry Python SDK
MCP SDK
pgvector
Redis
Celery
```

Those belong to later phases.

---

## Minimal Server Behavior

Implement a minimal FastAPI app.

Required endpoint:

```text
GET /health
```

Expected response:

```json
{
  "status": "ok",
  "service": "custodia-server"
}
```

Use `runtime.py` as the composition root.

Example shape:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Runtime:
    service_name: str


def build_runtime() -> Runtime:
    return Runtime(service_name="custodia-server")
```

`main.py` should expose:

```python
app
```

Do not put future business logic in `main.py`.

Routes should live under:

```text
custodia/interfaces/api/routes.py
```

---

## Settings

Create:

```text
server/src/custodia/app/settings.py
```

Use `pydantic-settings`.

The settings object should include at least:

```text
environment
service_name
database_url
keycloak_realm
keycloak_base_url
keycloak_client_id
jaeger_endpoint
```

Create:

```text
server/.env.example
```

With local development values:

```env
CUSTODIA_ENV=local
CUSTODIA_SERVICE_NAME=custodia-server

DATABASE_URL=postgresql://custodia:custodia@postgres:5432/custodia

KEYCLOAK_REALM=custodia
KEYCLOAK_BASE_URL=http://keycloak:8080
KEYCLOAK_CLIENT_ID=custodia-server

JAEGER_ENDPOINT=http://jaeger:4318
```

Do not commit real secrets.

---

## Docker Compose Foundation

Create root-level:

```text
docker-compose.yml
```

Add services:

```text
postgres
keycloak
jaeger
server
```

---

### Postgres

Use Postgres as the default database foundation.

Create:

```text
docker/postgres/init/001-create-databases.sql
```

Suggested databases:

```text
custodia
custodia_test
```

Use local development credentials only:

```text
user: custodia
password: custodia
```

Expose locally:

```text
5432
```

Use a named volume.

Do not create application tables yet.

---

### Keycloak

Add Keycloak for local OIDC/SSO development.

Create:

```text
docker/keycloak/realm/custodia-realm.json
```

Realm:

```text
custodia
```

Initial clients:

```text
custodia-server
custodia-client
```

Initial roles:

```text
admin
operations_manager
intake_coordinator
billing_staff
clinician
auditor
```

At least one local user if practical:

```text
admin@custodia.local
```

Use only local development credentials.

Expose Keycloak locally on a port that does not conflict with the backend. Prefer:

```text
8080
```

If needed, document alternative port.

---

### Jaeger

Add Jaeger for local trace visualization.

Expose Jaeger UI locally:

```text
16686
```

The server does not need to emit real traces yet. This is preparation for observability.

---

### Server

Create:

```text
server/Dockerfile
server/.dockerignore
```

The server container should run the FastAPI app and expose:

```text
8000
```

Expected local health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "custodia-server"
}
```

---

## Docs and Client Placeholders

Create:

```text
docs/README.md
docs/architecture/.gitkeep
docs/decisions/.gitkeep
client/README.md
```

Do not initialize the TypeScript frontend yet unless it is trivial and does not distract from Phase 0.

Frontend implementation starts later.

---

## Testing

Add minimal tests.

Required:

```text
server/tests/unit/test_runtime.py
```

It should verify that:

```text
build_runtime()
```

returns a runtime with:

```text
service_name == "custodia-server"
```

Optional:

Add a simple API test for:

```text
GET /health
```

Use FastAPI TestClient or httpx if clean.

For foundation phases, use only:

```text
unit tests
integration tests
```

Do not add browser E2E tests.

Agent evaluations come later.

---

## Architecture Requirements

Follow `AGENTS.md`.

Important rules:

1. `domain` must not import FastAPI, database, LLM, Keycloak, MCP, or infrastructure.
2. `application` must remain independent from FastAPI and concrete infrastructure.
3. `interfaces/api` owns FastAPI routes.
4. `infrastructure` owns concrete adapters.
5. `app/runtime.py` wires dependencies explicitly.
6. Do not use a dependency injection framework.
7. Do not add real business behavior yet.
8. Do not add PHI sample data.
9. Keep code typed and boring.
10. Keep route handlers thin.

---

## Acceptance Criteria

The task is complete when:

* Root folders exist:

  * `docs/`
  * `client/`
  * `server/`
* `server/` contains a valid Python project.
* `server/pyproject.toml` is configured.
* `src/custodia/` package exists with the expected architecture folders.
* `GET /health` works locally.
* `runtime.py` exists and is used.
* `server/.env.example` exists.
* `docker-compose.yml` exists.
* Docker Compose includes:

  * Postgres
  * Keycloak
  * Jaeger
  * Server
* At least one unit test passes.
* Ruff can run.
* Mypy can run.
* No unnecessary dependencies are added.
* No real secrets are committed.
* No business logic is implemented prematurely.

Expected commands:

```bash
cd server
uv sync
uv run pytest
uv run ruff check .
uv run mypy .
```

Docker:

```bash
docker compose up --build
```

Health check:

```bash
curl http://localhost:8000/health
```

---

## What Not To Do

Do not implement:

* Intake Agent,
* Policy Agent,
* Daily Briefing,
* Postgres repositories,
* audit tables,
* Keycloak JWT validation,
* real observability instrumentation,
* MCP server,
* TypeScript frontend,
* MinIO,
* Redis,
* workers,
* LangChain,
* LangGraph,
* LLM providers,
* vector store,
* clinical logic.

This is only the Phase 0 foundation.

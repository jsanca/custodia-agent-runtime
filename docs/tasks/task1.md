# Task: Initialize Custodia Server Project Skeleton

## Context

We are building **Custodia**, a guarded AI operations layer for mental health administration.

Repository name:

```text
custodia-agent-runtime
```

Top-level repository layout should be:

```text
docs/
client/
server/
README.md
AGENTS.md
```

This task focuses only on creating the initial **Python server skeleton** under `server/`.

The project follows a **hexagonal-inspired, Go-like Python architecture**:

* small Python protocols instead of large Java-style interfaces,
* explicit runtime composition,
* domain/application separated from infrastructure,
* FastAPI only at the boundary,
* no business logic in API routes,
* tests with fakes,
* audit/observability/security considered from the beginning.

Read `README.md` and `AGENTS.md` before implementing.

---

## Goal

Create the initial Python backend project structure under:

```text
server/
```

The goal is not to implement business behavior yet. The goal is to establish a clean, idiomatic Python foundation that future phases can build on.

---

## Expected Layout

Create this structure:

```text
server/
  pyproject.toml
  README.md

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

## Tooling

Use a modern Python project configuration.

Prefer `uv` as the package/project manager.

Configure `pyproject.toml` with:

* Python 3.12+
* FastAPI
* Pydantic
* pydantic-settings
* pytest
* ruff
* mypy

Do not add LLM providers, LangChain, LangGraph, vector databases, SQLAlchemy, OpenTelemetry, or MCP dependencies yet.

This task is only the foundation.

---

## Minimal Behavior

Implement a minimal FastAPI app.

`custodia/app/main.py` should expose an `app` object.

The API should have a basic health endpoint:

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

Use `runtime.py` as the composition root, even if the runtime is still minimal.

Example concept:

```python
@dataclass(frozen=True)
class Runtime:
    service_name: str


def build_runtime() -> Runtime:
    return Runtime(service_name="custodia-server")
```

The API route should not hardcode future business logic.

---

## Architectural Requirements

Follow these rules:

1. Keep `domain` free of FastAPI, database, LLM, Keycloak, MCP, and infrastructure imports.
2. Keep `application` independent from FastAPI and concrete infrastructure.
3. Use `runtime.py` for explicit composition.
4. Keep route handlers thin.
5. Do not introduce dependency injection frameworks.
6. Do not create generic repositories yet.
7. Do not create fake business complexity.
8. Do not add real LLM, RAG, database, Keycloak, MCP, or OpenTelemetry implementations in this task.
9. Keep the skeleton boring, typed, and easy to extend.
10. Add tests for the minimal runtime and/or health endpoint.

---

## Testing

Add a minimal test that verifies either:

* `build_runtime()` returns a valid runtime, or
* `/health` returns the expected payload.

Prefer simple unit tests for this first task.

Do not add E2E/browser tests.

For foundation phases, we are using only the first two levels of the testing pyramid:

```text
unit tests
integration tests
```

Evaluation tests will come later as an additional layer for LLM behavior.

---

## Acceptance Criteria

The task is complete when:

* `server/` contains a valid Python project skeleton.
* `pyproject.toml` is configured.
* `src/custodia/` package exists with the expected architectural folders.
* `GET /health` works.
* `runtime.py` exists and is used.
* At least one test passes.
* Ruff and mypy can be run.
* No unnecessary AI/vector/DB dependencies are added.
* Architecture boundaries from `AGENTS.md` are respected.

---

## What Not To Do

Do not:

* implement the Intake Agent yet,
* add real Postgres integration,
* add Keycloak yet,
* add LangChain or LangGraph yet,
* add MCP yet,
* add frontend code,
* add clinical logic,
* add PHI sample data,
* put business logic in FastAPI routes,
* create a giant `main.py`,
* over-engineer the skeleton.

This task should produce a clean foundation for Phase 0 only.

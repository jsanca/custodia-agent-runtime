# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Read `AGENTS.md` before making changes — it defines all architecture rules, coding standards, and healthcare safety boundaries in detail.

---

## Project Layout

```
custodia-agent-runtime/
  server/        # Python backend (FastAPI, hexagonal architecture)
  client/        # TypeScript frontend (operations console)
  docs/          # Architecture docs and task specs
  AGENTS.md      # Detailed architecture and coding rules
```

---

## Development Commands

### Backend (server/)

```bash
# Start infrastructure (Postgres, Keycloak, OTEL, Jaeger)
docker compose up -d

cd server
uv sync                                          # install dependencies
uv run fastapi dev src/custodia/app/main.py      # run dev server

uv run pytest                                    # run all tests
uv run pytest tests/unit/test_runtime.py         # run a single test file
uv run pytest -k "test_health"                   # run tests matching a name

uv run ruff check .                              # lint
uv run mypy .                                    # type check
```

### Frontend (client/)

```bash
cd client
npm install
npm run dev
```

---

## Architecture

Custodia uses a **hexagonal-inspired, Go-like Python architecture**. The core rule:

> Interfaces call application use cases → use cases depend on small protocols → infrastructure implements those protocols → `runtime.py` composes everything explicitly.

### Dependency direction

```
interfaces  →  application  →  domain
infrastructure  →  application/domain protocols
app/runtime.py  →  everything (composition root only)
```

### Layer responsibilities

| Layer | Location | Purpose |
|---|---|---|
| `domain` | `src/custodia/domain/` | Frozen dataclasses, StrEnums, no framework imports |
| `application` | `src/custodia/application/` | Use cases and workflows; depends on `typing.Protocol` ports |
| `infrastructure` | `src/custodia/infrastructure/` | Concrete adapters: LLM, DB, auth, RAG, observability |
| `interfaces` | `src/custodia/interfaces/` | FastAPI routes, scheduled jobs, MCP server |
| `app` | `src/custodia/app/` | `runtime.py` wires everything; `settings.py` reads env vars |

### Key patterns

- **Ports**: small `typing.Protocol` classes named after what they do (e.g., `LoadsPatientAdministrativeProfile`, `GeneratesText`)
- **Runtime**: `build_runtime()` in `runtime.py` manually instantiates all concrete adapters and injects them — no DI container
- **Fakes**: use `FakeLlm`, `FakeAuth`, etc. in tests; application services must not require real infrastructure
- **Audit**: compliance-relevant events (e.g., `INTAKE_AGENT_ANSWERED`, `MCP_TOOL_INVOKED`) are written via `SavesAuditEvents` protocol, separate from structured logs

### Current phase

**Phase 0 — Project Skeleton.** See `docs/tasks/task1.md` for the active task spec. Do not add real LLM, Postgres, Keycloak, vector store, or MCP implementations until Phase 1+.

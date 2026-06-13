# AGENTS.md

Architecture rules, hard constraints, and repo conventions for Custodia. Companion file: `CLAUDE.md` (Claude Code).

---

## Project Layout

```
server/        # Python backend (uv, FastAPI, hexagonal architecture)
client/        # TypeScript frontend (no code yet)
docker/        # Docker Compose: Postgres, Keycloak, Jaeger
docs/          # Architecture docs, decision records, task specs
```

**All backend commands run from `server/`.**

---

## Commands (run from `server/`)

```bash
docker compose up -d                           # start infra (Postgres, Keycloak, Jaeger)
uv sync                                        # install dependencies
uv run fastapi dev src/custodia/app/main.py    # dev server (hot reload on port 8000)
uv run ruff check .                            # lint
uv run mypy .                                  # type check (strict mode)
uv run pytest                                  # all tests
uv run pytest tests/unit/test_runtime.py       # single test file
uv run pytest -k "test_health"                 # tests matching name
```

---

## Architecture

Hexagonal, Go-style. Layer dependencies flow inward:

```
interfaces  →  application  →  domain
infrastructure  →  application/domain protocols only
app/runtime.py  →  composition root (wires everything)
```

### Layer import rules

| Layer | May import | Must NOT import |
|---|---|---|
| `domain` | stdlib, each other | application, infrastructure, interfaces, any framework (FastAPI, SQLAlchemy, LLM SDKs, Keycloak, MCP) |
| `application` | domain, `typing.Protocol` | infrastructure, interfaces |
| `infrastructure` | domain | application services |
| `interfaces` | application, DTOs | — (must not contain business logic) |
| `app` | everything (composition only) | — |

### Patterns

- **Ports**: small `typing.Protocol` classes in `application/ports.py`, named after role: `LoadsPatientAdministrativeProfile`, `GeneratesText`, `SavesAuditEvents`, `RetrievesPolicyContext`, `AppliesAgentGuardrails`
- **Runtime composition**: `build_runtime()` in `app/runtime.py` manually instantiates and wires all adapters — no DI container
- **Services**: depend on protocols, never on concrete infrastructure. Never instantiate DB clients, LLM SDKs, or HTTP clients in service constructors.
- **Route handlers**: thin — validate input, delegate to application service, return DTO. No business logic in routes.
- **Domain objects**: `@dataclass(frozen=True)`, `StrEnum` for symbolic values. Map DB rows → domain objects explicitly; ORM models are not domain objects.
- **Duplicate nothing**: API routes, jobs, and MCP tools all call the same application services.

---

## Current Phase — Phase 0 (Project Skeleton)

**Only FAKE implementations exist. Do NOT add real LLM, Postgres, Keycloak, vector store, or MCP implementations.**

| Type | Files |
|---|---|
| **FAKE** | `FakeLlm` — hardcoded strings<br>`FakePrincipal` — hardcoded staff user<br>`InMemoryPatientRepository` — seeds PAT-001 (complete), PAT-002 (missing docs)<br>`InMemoryAuditRepository` — append-only list<br>`KeywordPolicyRetriever` — keyword matching, no embeddings |
| **STUB** (empty `__init__.py`) | `infrastructure/observability/`, `interfaces/jobs/`, `interfaces/mcp/` |

Active task specs: `docs/tasks/`.

---

## Testing

- `pytest-asyncio` is in `auto` mode — no `@pytest.mark.asyncio` marker needed for async tests (use it explicitly only when `scope` is required)
- HTTP tests: `httpx.AsyncClient(transport=ASGITransport(app=app))` — no real server
- Inject pre-built `Runtime` via `create_app(runtime=...)` for test isolation
- Application service tests use fakes only — never real LLMs, Keycloak, or network
- Concrete adapter tests → `tests/integration/`. LLM behavior evals → `tests/evals/`.

---

## Naming Conventions

Favor explicit names that describe *responsibility*, not implementation type. This is a learning-project convention.

- **Constructor parameters**: name after the protocol role, not a vague noun or implementation class. Prefer `patient_profile_loader`, `policy_context_retriever`, `text_generator`, `audit_recorder`, `agent_guardrail` over `profiles`, `policies`, `llm`, `audit`, `guardrails`
- **Loop variables in comprehensions**: descriptive (`document` not `d`)
- **Result variables**: describe what it contains (`missing_document_names`, `retrieved_policy_chunks`, `raw_llm_answer`, `guarded_answer` — not `missing`, `chunks`, `raw`, `answer2`)

---

## Healthcare Guardrails (Hard Constraints)

**Must NOT:**
- diagnose, recommend treatment, or replace clinicians
- assess self-harm risk
- make final clinical decisions
- let LLMs decide authorization or bypass deterministic business rules

**May:** summarize administrative status, retrieve policies, draft messages, classify missing documents, flag items for human review.

Guardrail checks in `application/guardrails.py` use keyword-based detection. When unsure, require human review.

---

## PHI Boundaries

Must never appear in logs or prompts: raw PHI (names, identifiers beyond patient IDs), full prompts/LLM responses (by default), access tokens, secrets, API keys.

Audit events and observability traces are separate concerns.

---

## Audit Events

Defined in `domain/audit.py`. Separate from structured logs. Each event records: who did what to which resource, outcome, and human-review flag. Do not store raw PHI in audit metadata.

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

All backend commands run from `server/`.

```bash
# Start infrastructure (Postgres, Keycloak, OTEL, Jaeger)
docker compose up -d

cd server
uv sync                                          # install dependencies
uv run fastapi dev src/custodia/app/main.py      # run dev server (port 8000)

uv run pytest                                    # run all tests
uv run pytest tests/unit/test_runtime.py         # run a single test file
uv run pytest -k "test_health"                   # run tests matching a name

uv run ruff check .                              # lint
uv run mypy .                                    # type check (strict mode)
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

### Layer import rules

| Layer | May import | Must NOT import |
|---|---|---|
| `domain` | stdlib only | application, infrastructure, interfaces, any framework |
| `application` | domain, `typing.Protocol` | infrastructure, interfaces |
| `infrastructure` | domain | application services |
| `interfaces` | application, DTOs | must not contain business logic |
| `app` | everything | — (composition only) |

### Key patterns

- **Ports**: small `typing.Protocol` classes in `application/ports.py`, named after role: `LoadsPatientAdministrativeProfile`, `GeneratesText`, `SavesAuditEvents`, `RetrievesPolicyContext`, `AppliesAgentGuardrails`
- **Runtime**: `build_runtime()` in `runtime.py` manually instantiates all concrete adapters and injects them — no DI container
- **Fakes**: use `FakeLlm`, `FakeAuth`, etc. in tests; application services must not require real infrastructure
- **Audit**: compliance-relevant events (e.g., `INTAKE_AGENT_ANSWERED`, `MCP_TOOL_INVOKED`) are written via `SavesAuditEvents` protocol, separate from structured logs
- **Routes**: thin — validate input, delegate to application service, return DTO. No business logic in routes.

### Current phase

**Phase 0 — Project Skeleton.** See `docs/tasks/` for active task specs. Do not add real LLM, Postgres, Keycloak, vector store, or MCP implementations until Phase 1+.

Active fake/in-memory implementations:
- `FakeLlm` — hardcoded strings; tracks `last_prompt` for testing
- `FakePrincipal` — hardcoded staff user
- `InMemoryPatientRepository` — seeds PAT-001 (complete), PAT-002 (missing docs)
- `InMemoryAuditRepository` — append-only list
- `KeywordPolicyRetriever` — keyword matching, no embeddings

---

## Testing

- `pytest-asyncio` is in `auto` mode — no `@pytest.mark.asyncio` needed for async tests (use it explicitly only when `scope` is required)
- HTTP tests use `httpx.AsyncClient(transport=ASGITransport(app=app))` — no real server
- Inject a pre-built `Runtime` via `create_app(runtime=...)` for test isolation
- Application service tests use fakes only — never real LLMs, Keycloak, or network calls
- Concrete adapter tests → `tests/integration/`. LLM behavior evals → `tests/evals/`.

---

## Healthcare Safety Constraints (Hard Limits)

**Must NOT:**
- Diagnose, recommend treatment, or replace clinicians
- Assess self-harm risk
- Make final clinical decisions
- Let LLMs decide authorization or bypass deterministic business rules

**May:** Summarize administrative status, retrieve policies, draft messages, classify missing documents, flag items for human review.

Guardrail checks in `application/guardrails.py` use keyword-based detection. When in doubt, require human review.

### PHI Boundaries

Must never appear in logs, prompts, or audit metadata: raw PHI (names, identifiers beyond patient IDs), full LLM prompts/responses, access tokens, secrets, or API keys.

---

## Naming Guidelines

Custodia favors explicit, readable names over short clever names. The project is also used to learn idiomatic Python from a Java/Go background, so names should make each object's role clear at the call site.

**Prefer names that describe responsibility:**

```python
# Good
patient_profile_loader
policy_context_retriever
text_generator
audit_recorder
agent_guardrail
missing_document_names
pending_review_document_names
retrieved_policy_chunks
raw_llm_answer
guarded_answer

# Avoid
llm, audit, svc, repo, ctx, d, res, obj
missing, pending, chunks, raw, answer2
```

**Constructor parameters — name after the protocol role:**

```python
# Good
def __init__(
    self,
    patient_profile_loader: LoadsPatientAdministrativeProfile,
    policy_context_retriever: RetrievesPolicyContext,
    text_generator: GeneratesText,
    audit_recorder: SavesAuditEvents,
    agent_guardrail: AppliesAgentGuardrails,
) -> None:

# Avoid: profiles, policies, llm, audit, guardrails
```

**List comprehensions — use descriptive loop variables:**

```python
# Good
missing_document_names = [
    document.name
    for document in patient_profile.documents
    if document.status == IntakeStatus.MISSING
]

# Avoid
missing = [d.name for d in profile.documents if d.status == IntakeStatus.MISSING]
```

**Rule of thumb:** If a name requires inspecting the type annotation or implementation to understand what it means, choose a more explicit name.

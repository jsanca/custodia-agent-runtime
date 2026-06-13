# AGENTS.md

Architecture rules and hard constraints for Custodia. See `CLAUDE.md` for dev commands and operational quick-start.

---

## Architecture

Custodia follows a **hexagonal, Go-style** pattern (not Spring/Java):

```
interfaces  →  application  →  domain
infrastructure  →  application/domain protocols
server/src/custodia/app/runtime.py  →  composition root (wires everything)
```

The backend lives under `server/` (not `backend/`). The frontend lives under `client/`.

### Layer import rules

- `domain` — must not import from application, infrastructure, interfaces, or any framework (FastAPI, SQLAlchemy, LLM SDKs, Keycloak, MCP)
- `application` — may import `domain` and define `typing.Protocol` ports; must not import infrastructure or interfaces
- `infrastructure` — may import `domain` and implement application protocols; should not import application services
- `interfaces` — may import `application` and DTOs; must not contain business logic
- `app/runtime.py` — may import everything (composition only)

---

## Protocols (Ports)

Protocols must be **small** and named after what the consumer needs:

```python
class LoadsPatientAdministrativeProfile(Protocol):
    def load(self, patient_id: str) -> PatientAdministrativeProfile | None: ...

class GeneratesText(Protocol):
    def generate(self, prompt: str) -> str: ...
```

Never create large catch-all interfaces (e.g., a `PatientRepository` with `save`/`load`/`delete`/`find_all`/`find_by_email`). A concrete adapter may implement several small protocols, but each use case depends only on the capabilities it needs.

---

## Domain Models

- Use `@dataclass(frozen=True)` for domain objects
- Use `StrEnum` for symbolic values
- Never put database sessions, HTTP clients, FastAPI request objects, or LLM SDK objects in domain models
- Map DB rows → domain objects explicitly; don't let ORM models become domain objects

---

## Application Services

Application services depend on protocols, never on concrete infrastructure:

```python
class IntakeAgentService:
    def __init__(
        self,
        profiles: LoadsPatientAdministrativeProfile,
        llm: GeneratesText,
        audit: SavesAuditEvents,
        guardrails: AppliesAgentGuardrails,
    ): ...
```

They must not instantiate database clients, LLM SDKs, Keycloak validators, or HTTP clients directly.

---

## Runtime Composition

Use **manual DI** in `runtime.py` — no DI container:

```python
def build_runtime() -> Runtime:
    profiles = InMemoryPatientRepository()
    llm = FakeLlm()
    audit = PostgresAuditRepository(...)
    guardrails = DefaultAgentGuardrails()
    intake_agent = IntakeAgentService(profiles=profiles, llm=llm, audit=audit, guardrails=guardrails)
    return Runtime(intake_agent=intake_agent)
```

Keep it boring, explicit, and readable.

---

## Testing

- Application service tests use fakes (`FakeLlm`, `FakeAuth`, in-memory repos) — never real LLM APIs, Keycloak, or network
- Concrete adapter tests (Postgres, API) go in integration tests
- LLM behavior evaluations live under `server/tests/evals/`

---

## PHI and Logging Boundaries

**Must never appear in logs or prompts:**
- raw PHI (names, identifiers beyond patient IDs)
- full prompts (by default)
- full LLM responses (by default)
- access tokens, secrets, API keys

Logs should be structured and include trace IDs, agent run IDs, and tool names — not personal data. Audit events and observability traces are separate concerns.

---

## Audit Events

Audit records compliance-relevant business events (separate from structured logging). Events convey who did what to which resource, with outcome and human-review flag. Do not store raw PHI in audit metadata.

---

## Healthcare Guardrails (Hard Constraints)

**The system must not:**
- diagnose, recommend treatment, or replace clinicians
- assess self-harm risk
- make final clinical decisions
- let LLMs decide authorization or bypass deterministic business rules

**The system may:**
- summarize administrative status, retrieve policies, draft messages
- classify missing documents, suggest operational next steps
- flag items for human review

Guardrail checks must be explicit and testable. When unsure, require human review.

---

## Tools and Commands

- Package manager: `uv`
- Lint: `ruff check .`
- Type check: `mypy .`
- Test: `pytest` (single test: `pytest -k "name"`)
- Dev server: `fastapi dev`
- See `CLAUDE.md` for full command reference.

---

## Current Phase

**Phase 0 — Project Skeleton.** Only the minimal FastAPI app, runtime composition, domain stubs, and test infrastructure exist. Do not add real LLM, Postgres, Keycloak, vector store, or MCP implementation until later phases. Active task specs live in `docs/tasks/`.

---

## Key Principles

1. Deterministic code first, AI only where it adds value
2. Audit every compliance-relevant action
3. Never duplicate business logic across API routes, jobs, and MCP tools — all call the same application services
4. Route handlers must be thin (validate, delegate to application service, return DTO)
5. Keep PHI out of logs and prompts
6. Require human review for sensitive actions
7. Write tests with fakes before using real providers

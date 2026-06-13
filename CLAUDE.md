# AGENTS.md

Guidance for AI coding agents working on **Custodia**.

Custodia is a guarded AI operations layer for mental health administration. It is a Python-first, TypeScript-supported reference implementation for production-oriented administrative agents in behavioral health operations.

This document defines how agents should understand, extend, and protect the project.

---

## 1. Project Mission

Custodia exists to explore how AI agents can safely assist administrative workflows in mental health organizations.

The system should help with:

- intake readiness,
- internal policy retrieval,
- administrative briefings,
- insurance/admin workflow support,
- task discovery,
- MCP-based operational tooling,
- audit-first AI automation.

The system must not:

- diagnose patients,
- recommend treatment,
- replace clinicians,
- automate clinical judgment,
- expose PHI unnecessarily,
- log sensitive patient information,
- execute sensitive actions without proper authorization and review.

Guiding principle:

> Custodia is not a chatbot. It is a guarded operational layer where deterministic workflows, AI-assisted agents, RAG, auditability, observability, MCP tools, and human review work together to reduce administrative burden.

---

## 2. Architectural Style

Custodia uses a **hexagonal-inspired, Go-like Python architecture**.

Do not write Python as loose scripts.
Do not recreate Spring-style Java architecture.
Do not hide everything behind framework magic.

Use:

- small protocols,
- explicit runtime composition,
- clear application use cases,
- domain models without infrastructure dependencies,
- adapters at the edges,
- tests with fakes,
- typed code,
- deterministic workflows first,
- AI-assisted steps only where they add value.

Architecture rule:

> Interfaces call application use cases. Use cases depend on small protocols. Infrastructure implements those protocols. `runtime.py` composes everything explicitly.

---

## 3. Expected Repository Layout

The intended layout is:

```text
custodia-agent-runtime/
  backend/
    src/
      custodia/
        app/
          main.py
          runtime.py
          settings.py

        domain/
          identity.py
          patients.py
          intake.py
          tasks.py
          audit.py
          agents.py

        application/
          ports.py
          intake_agent.py
          policy_agent.py
          daily_briefing.py
          guardrails.py

        infrastructure/
          identity/
            keycloak_validator.py
            fake_auth.py

          persistence/
            postgres.py
            patient_repository.py
            audit_repository.py
            task_repository.py

          rag/
            text_chunker.py
            keyword_retriever.py
            vector_retriever.py

          llm/
            fake_llm.py
            openai_llm.py

          observability/
            tracing.py
            logging.py

        interfaces/
          api/
            routes.py
            middleware.py

          jobs/
            daily_admin_briefing_job.py

          mcp/
            server.py

    tests/
      unit/
      integration/
      evals/

  frontend/
    src/
      app/
      components/
      pages/
      api/

  docker/
    keycloak/
    postgres/
    otel/

  docs/
    architecture/
    decisions/
```

Keep this structure coherent. If a new package is needed, make sure it represents a real architectural boundary.

---

## 4. Dependency Direction

Respect this dependency direction:

```text
interfaces  -> application -> domain
infrastructure -> application/domain protocols
app/runtime -> everything for composition only
```

Rules:

- `domain` must not import from `application`, `infrastructure`, `interfaces`, FastAPI, SQLAlchemy, OpenAI SDKs, Keycloak clients, MCP SDKs, or framework code.
- `application` may import `domain` and define/use small protocols.
- `infrastructure` may import `domain` and implement application protocols.
- `interfaces` may import `application` and request/response DTOs.
- `app/runtime.py` is the composition root and may wire concrete implementations.
- FastAPI belongs in `interfaces/api`, not in domain/application.
- Database code belongs in `infrastructure/persistence`, not in application/domain.
- LLM provider code belongs in `infrastructure/llm`, not in agent services directly.
- MCP implementation belongs in `interfaces/mcp`, not in domain/application.

---

## 5. Python Design Principles

Use modern, explicit Python.

Prefer:

- `dataclasses` for immutable domain models,
- `pydantic` for API request/response DTOs and settings,
- `typing.Protocol` for small ports,
- `Enum` or `StrEnum` for stable symbolic values,
- explicit return types,
- small modules,
- small classes,
- pure functions where useful,
- dependency injection by constructor,
- explicit runtime wiring.

Avoid:

- global mutable state,
- service locators,
- hidden dependency injection frameworks,
- large abstract base classes,
- generic repositories with too many methods,
- framework imports in domain,
- implicit environment variable reads inside business logic,
- untyped dictionaries as long-lived domain objects,
- logging prompts or PHI,
- catching broad exceptions without preserving context.

---

## 6. Protocols and Ports

Protocols should be small and consumer-oriented.

Good:

```python
from typing import Protocol

from custodia.domain.patients import PatientAdministrativeProfile


class LoadsPatientAdministrativeProfile(Protocol):
    def load(self, patient_id: str) -> PatientAdministrativeProfile | None:
        ...
```

Good:

```python
class RetrievesPolicyContext(Protocol):
    def retrieve(self, query: str) -> list[ContextChunk]:
        ...
```

Avoid large Java-style interfaces:

```python
class PatientRepository(Protocol):
    def save(self, patient): ...
    def load(self, patient_id): ...
    def delete(self, patient_id): ...
    def find_all(self): ...
    def find_by_email(self, email): ...
    def find_by_status(self, status): ...
```

A concrete adapter may implement several small protocols, but a use case should only depend on the capabilities it needs.

---

## 7. Domain Models

Domain models should be boring, typed, and framework-free.

Use frozen dataclasses when possible:

```python
from dataclasses import dataclass
from enum import StrEnum


class IntakeStatus(StrEnum):
    MISSING = "missing"
    COMPLETE = "complete"
    PENDING_REVIEW = "pending_review"


@dataclass(frozen=True)
class IntakeDocument:
    name: str
    status: IntakeStatus


@dataclass(frozen=True)
class PatientAdministrativeProfile:
    patient_id: str
    display_name: str
    preferred_language: str
    requested_service: str
    documents: list[IntakeDocument]
```

Do not put database sessions, HTTP clients, FastAPI request objects, or LLM SDK objects inside domain models.

---

## 8. Application Services and Use Cases

Application services implement business/application workflows.

They should:

- depend on protocols,
- be easy to test with fakes,
- return explicit domain/application result objects,
- audit compliance-relevant actions,
- call guardrails before returning AI-assisted results,
- avoid framework-specific code.

Example shape:

```python
class IntakeAgentService:
    def __init__(
        self,
        profiles: LoadsPatientAdministrativeProfile,
        policies: RetrievesPolicyContext,
        llm: GeneratesText,
        audit: SavesAuditEvents,
        guardrails: AppliesAgentGuardrails,
    ):
        self._profiles = profiles
        self._policies = policies
        self._llm = llm
        self._audit = audit
        self._guardrails = guardrails

    def answer_question(self, principal: Principal, patient_id: str, question: str) -> AgentAnswer:
        ...
```

Do not let application services directly instantiate:

- database clients,
- LLM SDK clients,
- Keycloak validators,
- vector stores,
- HTTP clients,
- FastAPI response objects.

Those belong in infrastructure and runtime composition.

---

## 9. Runtime Composition

Use `app/runtime.py` as the explicit composition root.

This project should use manual dependency injection, similar to Go.

Example:

```python
from dataclasses import dataclass

from custodia.application.intake_agent import IntakeAgentService


@dataclass(frozen=True)
class Runtime:
    intake_agent: IntakeAgentService


def build_runtime() -> Runtime:
    profiles = InMemoryPatientRepository()
    policies = KeywordPolicyRetriever()
    llm = FakeLlm()
    audit = PostgresAuditRepository(...)
    guardrails = DefaultAgentGuardrails()

    intake_agent = IntakeAgentService(
        profiles=profiles,
        policies=policies,
        llm=llm,
        audit=audit,
        guardrails=guardrails,
    )

    return Runtime(intake_agent=intake_agent)
```

Do not introduce a dependency injection container unless there is a strong reason.

The runtime should be explicit, readable, and boring.

---

## 10. Interfaces

Interfaces are delivery mechanisms.

Initial interfaces:

- FastAPI API,
- scheduled jobs,
- MCP tools,
- TypeScript frontend.

All of these should call the same application use cases.

Do not duplicate business logic across API routes, jobs, and MCP tools.

Correct:

```text
API route -> IntakeAgentService
MCP tool -> IntakeAgentService
Scheduled job -> DailyBriefingService
```

Incorrect:

```text
API route has its own intake logic
MCP tool has duplicated intake logic
Job has a third version of the same logic
```

---

## 11. FastAPI Guidelines

FastAPI should stay at the boundary.

Use it for:

- routing,
- request validation,
- response DTOs,
- dependency extraction,
- auth middleware/dependencies,
- HTTP error mapping.

Do not put core business logic in route handlers.

Good route shape:

```python
@router.post("/intake/ask")
async def ask_intake_question(request: AskIntakeQuestionRequest) -> AskIntakeQuestionResponse:
    result = runtime.intake_agent.answer_question(
        principal=request.principal,
        patient_id=request.patient_id,
        question=request.question,
    )
    return AskIntakeQuestionResponse.from_result(result)
```

The actual project may use FastAPI dependencies to inject `Runtime` and `Principal`.

---

## 12. Persistence

Postgres is the default relational database.

Use Postgres for:

- administrative profiles,
- tasks,
- audit events,
- agent runs,
- daily briefings,
- workflow execution status.

Use `pgvector` or a dedicated vector store later for embeddings.

Persistence rules:

- repositories live under `infrastructure/persistence`,
- repository methods should implement small application protocols,
- database models should not become domain models by accident,
- map database rows to domain objects explicitly,
- keep transaction boundaries visible,
- do not hide important write operations inside LLM/tool code.

---

## 13. Auditability

Auditability is not logging.

Audit records compliance-relevant business events.

Examples:

- `INTAKE_PROFILE_VIEWED`
- `INTAKE_AGENT_ANSWERED`
- `POLICY_CONTEXT_RETRIEVED`
- `DAILY_BRIEFING_GENERATED`
- `MCP_TOOL_INVOKED`
- `ADMIN_TASK_CREATED`
- `HUMAN_REVIEW_REQUIRED`
- `TOOL_CALL_DENIED`
- `TOOL_CALL_COMPLETED`

Audit events should include, when available:

- actor subject,
- actor email,
- actor roles,
- action,
- resource type,
- resource id,
- agent name,
- tool name,
- outcome,
- human review flag,
- trace id,
- metadata.

Do not store raw PHI in audit metadata unless there is a deliberate, reviewed reason.

Prefer identifiers and minimal context.

---

## 14. Observability

Observability explains system behavior.

Use OpenTelemetry for:

- HTTP request traces,
- scheduled job traces,
- MCP tool traces,
- agent run traces,
- RAG retrieval traces,
- LLM call traces,
- tool call traces,
- workflow step traces.

Logs should be structured and should include:

- request id,
- trace id,
- agent run id,
- workflow id,
- tool name,
- outcome,
- latency where useful.

Logs must not include:

- raw PHI,
- full prompts by default,
- full LLM responses by default,
- patient names unless explicitly approved for a demo-only fake dataset,
- access tokens,
- secrets,
- API keys.

---

## 15. Guardrails and Clinical Boundaries

Agents must respect the administrative scope of Custodia.

The system may:

- summarize administrative status,
- retrieve internal policy context,
- draft administrative messages,
- classify missing documents,
- suggest operational next steps,
- flag human review,
- explain workflow blockers.

The system must not:

- diagnose,
- provide therapy,
- recommend clinical treatment,
- assess self-harm risk,
- replace clinical supervision,
- make final clinical decisions.

Guardrail checks should be explicit and testable.

Examples:

- refuse clinical advice requests,
- mark sensitive actions as requiring human review,
- prevent unauthorized tool calls,
- restrict tool results to minimum necessary data,
- validate structured LLM outputs.

---

## 16. AI and LLM Usage

LLM code belongs behind ports.

Application services should depend on a protocol such as:

```python
class GeneratesText(Protocol):
    def generate(self, prompt: str) -> str:
        ...
```

or, for structured outputs:

```python
class GeneratesStructuredResponse(Protocol):
    def generate(self, request: LlmRequest) -> LlmResponse:
        ...
```

Provider-specific clients belong in:

```text
infrastructure/llm/
```

Rules:

- build prompts in application or dedicated prompt modules,
- never concatenate untrusted text into tool commands,
- validate structured outputs,
- keep model/provider replaceable,
- do not let LLMs decide authorization,
- do not let LLMs bypass deterministic business rules,
- do not log full prompts by default,
- do not send more PHI than necessary.

---

## 17. RAG Guidelines

RAG should be grounded and auditable.

RAG components:

- document loader,
- chunker,
- retriever,
- source metadata,
- answer generator,
- source references.

Initial implementation may use keyword retrieval.

Later implementations may use embeddings and `pgvector` or a dedicated vector database.

Rules:

- return source references,
- keep chunk metadata,
- test retrieval behavior,
- separate retrieval from generation,
- avoid using RAG as a substitute for deterministic data queries,
- do not embed unnecessary PHI unless the use case explicitly requires it.

Use deterministic queries for operational facts.
Use RAG for policies, procedures, and knowledge documents.

---

## 18. Deterministic Workflows

Not everything should be agentic.

Prefer deterministic workflows for:

- loading incomplete intakes,
- finding pending insurance verifications,
- finding overdue tasks,
- applying business rules,
- checking readiness status,
- determining whether human review is required.

Use AI for:

- summarization,
- explanation,
- drafting,
- policy-grounded Q&A,
- classification where deterministic rules are insufficient,
- turning structured data into clear operational briefings.

The Daily Administrative Briefing is mostly deterministic. The LLM should only help generate a readable summary and optional recommendations.

---

## 19. Durable Jobs and Workflows

Scheduled jobs and workflow steps should be explicit and observable.

A durable workflow should have:

- workflow id,
- execution status,
- step status,
- retry policy,
- failure reason,
- timestamps,
- audit events,
- trace id.

Do not implement long-running production workflows as one opaque function that fails all-or-nothing without state.

Initial versions may be simple, but the design should leave room for:

- retries,
- idempotency,
- status tracking,
- human review,
- compensation actions.

---

## 20. MCP Guidelines

MCP tools are sensitive system entrypoints.

Initial MCP tools should be read-only:

- `list_pending_intakes`,
- `get_patient_admin_summary`,
- `search_internal_policy`,
- `get_daily_admin_briefing`.

Rules:

- authenticate the caller,
- authorize each tool,
- minimize returned PHI,
- audit each tool call,
- return structured results,
- deny unsafe or unauthorized calls,
- avoid write-capable tools until authorization, audit, idempotency, and human review are implemented.

MCP tools should call application use cases, not infrastructure directly.

---

## 21. TypeScript Frontend Guidelines

The frontend is an operations console, not the core of the system.

Initial screens:

- daily briefing,
- pending intakes,
- patient administrative summary,
- agent runs,
- audit log.

Frontend rules:

- use TypeScript strictly,
- keep API types explicit,
- avoid duplicating backend business logic,
- show when a result is AI-assisted,
- show source references when available,
- show human review status,
- never expose hidden prompts or sensitive internal traces to regular users.

---

## 22. Testing Strategy

Tests are part of the architecture.

Use:

- unit tests for domain/application services,
- fake adapters for use case tests,
- integration tests for Postgres repositories,
- API tests for FastAPI boundaries,
- eval tests for agent behavior,
- guardrail tests for clinical boundaries,
- retrieval tests for RAG quality.

Application service tests should not require:

- real LLM APIs,
- real Keycloak,
- real vector database,
- network access.

Use fakes first.

Example fake:

```python
class FakeLlm:
    def __init__(self, response: str):
        self.response = response

    def generate(self, prompt: str) -> str:
        return self.response
```

---

## 23. Evaluation Harness

Custodia should include evaluation cases under:

```text
backend/tests/evals/
```

Evaluation should cover:

- grounded answers,
- policy source usage,
- non-clinical boundary behavior,
- refusal of clinical advice,
- PHI minimization,
- correct human review detection,
- suggested action correctness,
- RAG retrieval quality.

Evaluations should be repeatable and versioned.

Do not treat LLM behavior as untestable.

---

## 24. Code Style

Use:

- `ruff` for linting,
- `mypy` for type checking,
- `pytest` for tests,
- clear module names,
- explicit imports,
- explicit return types,
- meaningful dataclass names,
- small functions.

Avoid:

- clever metaprogramming,
- dynamic imports unless necessary,
- giant utility modules,
- catch-all `utils.py` dumping grounds,
- deep inheritance hierarchies,
- excessive decorators that hide control flow,
- monkeypatching core behavior outside tests.

Prefer boring code.

---

## 25. Error Handling

Use explicit errors where useful.

Application services should return meaningful result objects for expected business outcomes.

Examples:

- patient not found,
- unauthorized tool call,
- missing policy context,
- human review required,
- LLM response invalid,
- workflow step failed.

Do not swallow exceptions silently.

Do not expose internal stack traces to API/MCP consumers.

Do not include PHI in exception messages.

---

## 26. Configuration and Secrets

Use settings objects, not random environment variable reads across the codebase.

Settings belong in:

```text
app/settings.py
```

Rules:

- never commit secrets,
- never log secrets,
- inject settings through runtime composition,
- use `.env.example` for local development,
- keep provider-specific configuration in infrastructure adapters.

---

## 27. Documentation Expectations

When adding a major capability, update:

- `README.md` if it changes project scope, roadmap, or high-level architecture,
- `AGENTS.md` if it changes coding/architecture rules,
- `docs/architecture/` for diagrams or deeper explanations,
- `docs/decisions/` for architecture decisions.

Use Mermaid diagrams when they clarify flow or architecture.

---

## 28. Development Phases

The current roadmap is:

```text
Phase -1: Project Name and GitHub Repository
Phase 0: Project Skeleton
Phase 1: Intake Agent
Phase 2: RAG Over Internal Policies
Phase 3: Audit and Observability
Phase 4: Deterministic Jobs and Durable Workflows
Phase 5: MCP Tools
Phase 6: Real LLM and Vector Store
Phase 7: TypeScript Frontend Console
Phase 8: Evaluation Harness and Production Hardening
```

Agents should respect the phase currently being implemented.

Do not jump to complex frameworks before the simpler architecture is working.

---

## 29. What to Avoid

Avoid building:

- a generic chatbot,
- a clinical advice bot,
- an all-powerful autonomous agent,
- a LangChain/LangGraph demo without domain boundaries,
- a giant `main.py`,
- a framework-first application,
- a prompt-only architecture,
- an app where LLMs decide permissions,
- a system where audit is an afterthought,
- a system where logs leak PHI,
- a UI that hides whether a result is AI-assisted.

---

## 30. Implementation Heuristics

When unsure:

1. Put business concepts in `domain`.
2. Put workflows/use cases in `application`.
3. Put external details in `infrastructure`.
4. Put delivery mechanisms in `interfaces`.
5. Wire concrete implementations in `app/runtime.py`.
6. Use a small protocol instead of a large interface.
7. Use deterministic code before AI.
8. Add audit for compliance-relevant actions.
9. Add traces for operational visibility.
10. Keep PHI out of logs and prompts unless necessary.
11. Require human review for sensitive actions.
12. Write tests with fakes before using real providers.

---

## 31. Agent Operating Mode

AI coding agents working on this repository should:

- read `README.md` and `AGENTS.md` before making changes,
- preserve the architecture boundaries,
- make small, reviewable changes,
- add or update tests with every behavior change,
- avoid adding dependencies without a clear reason,
- prefer explicit Python over clever Python,
- document non-obvious decisions,
- keep healthcare safety boundaries visible,
- never introduce PHI into sample data unless fake and clearly labeled.

---

## 32. Final Principle

Build Custodia like a production system from day one, but evolve it in small slices.

The first working version should be simple:

```text
FastAPI endpoint
  -> application service
  -> fake repository
  -> fake retriever
  -> fake LLM
  -> audit event
  -> guarded response
```

Then replace adapters one by one.

That is the Custodia way.

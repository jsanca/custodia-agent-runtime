# Task: Phase 1 — Real Intake Agent

## Context

**Phase 0** established the project skeleton, hexagonal architecture, and all fake implementations (`FakeLlm`, `FakePrincipal`, `InMemoryPatientRepository`, `InMemoryAuditRepository`, `KeywordPolicyRetriever`).

**Phase 1** makes the Intake Agent real in the only way that matters: it calls a real LLM, and it is reachable through a real API endpoint. Everything else (auth, patient repo, audit persistence, vector search) remains fake/in-memory until its own phase.

Read `README.md`, `AGENTS.md`, and `CLAUDE.md` before implementing.

---

## Goal

Replace `FakeLlm` with a real Anthropic Claude adapter, and expose the Intake Agent via an HTTP endpoint that a real client can call.

The `IntakeAgentService` logic does not change. The application layer is already correct. Only the infrastructure (`AnthropicLlm`) and the interface layer (`routes.py`) change.

---

## What Changes

### New: `AnthropicLlm` adapter

Create:

```text
server/src/custodia/infrastructure/llm/anthropic_llm.py
```

It must implement the `GeneratesText` protocol:

```python
from anthropic import Anthropic

class AnthropicLlm:
    def generate(self, prompt: str) -> str:
        ...
```

- Model: `claude-sonnet-4-6` (configurable via settings)
- Use a single `user` message. System prompt: `"You are an administrative assistant for a behavioral health organization. Answer only administrative questions. Never give clinical advice."`
- Enable **prompt caching** on the system prompt (`cache_control: {"type": "ephemeral"}`).
- Max tokens: 1024.
- Do not add streaming yet.
- Return `content[0].text` from the response.

### New settings

Add to `CustodiaSettings`:

```text
ANTHROPIC_API_KEY       # required in non-local environments
LLM_MODEL               # default: "claude-sonnet-4-6"
LLM_MAX_TOKENS          # default: 1024
```

Update `server/.env.example` with placeholder values.

### Updated `build_runtime()`

Wire `AnthropicLlm` when `CUSTODIA_ENV != "local"`. In `"local"` (default) keep `FakeLlm` so local development and tests do not require an API key.

```python
if settings.env == "local":
    text_generator = FakeLlm()
else:
    text_generator = AnthropicLlm(settings)
```

### New: Intake Agent API route

Add to `server/src/custodia/interfaces/api/routes.py`:

```text
POST /api/v1/intake/{patient_id}/answer
```

Request body:

```json
{ "question": "What documents are missing?" }
```

Response body (on success):

```json
{
  "answer": "...",
  "requires_human_review": false,
  "suggested_actions": [
    { "description": "Collect missing documents: consent_form", "requires_human_review": false }
  ],
  "source_references": ["..."],
  "is_ai_assisted": true
}
```

Error responses:
- `404` if the patient ID is not found (`PatientNotFoundError`)
- `400` if `question` is blank

Auth: use `runtime.auth` (still `FakePrincipal`) to resolve the current principal. Real Keycloak JWT validation is Phase 2.

The route handler must remain thin — delegate entirely to `runtime.intake_agent.answer_question(...)`.

---

## What Does NOT Change

- `IntakeAgentService` logic — no modifications.
- `DefaultAgentGuardrails` — no modifications.
- `InMemoryPatientRepository` — stays in-memory. Real Postgres is Phase 2.
- `InMemoryAuditRepository` — stays in-memory. Real audit persistence is Phase 2.
- `KeywordPolicyRetriever` — stays keyword-based. Real vector search is Phase 3.
- `FakePrincipal` — stays. Real Keycloak JWT validation is Phase 2.
- Domain layer — no modifications.
- `FakeLlm` — stays, used when `CUSTODIA_ENV=local`.

---

## New Dependencies

Add only:

```text
anthropic>=0.40
```

Do not add `langchain`, `langgraph`, `openai`, or any other LLM framework.

---

## Testing

### Unit tests (no API key required)

All unit tests continue using `FakeLlm`. No test should require `ANTHROPIC_API_KEY`.

Add unit tests for the new route in `tests/unit/test_runtime.py` (or a new `tests/unit/test_intake_route.py`):

- `POST /api/v1/intake/PAT-001/answer` with a valid question → 200, `is_ai_assisted=True`
- `POST /api/v1/intake/PAT-UNKNOWN/answer` → 404
- `POST /api/v1/intake/PAT-001/answer` with blank question → 400

### Integration tests (require API key)

Add to `tests/integration/test_anthropic_llm.py`:

- Instantiate `AnthropicLlm` and call `generate("What is 2+2?")`.
- Assert the response is a non-empty string.
- Guard with `pytest.importorskip` or a skip marker when `ANTHROPIC_API_KEY` is not set.

These tests are not run in CI by default. Run them manually with:

```bash
CUSTODIA_ENV=dev uv run pytest tests/integration/
```

---

## Acceptance Criteria

- [ ] `AnthropicLlm` exists and implements `GeneratesText`.
- [ ] Prompt caching is enabled on the system prompt.
- [ ] `build_runtime()` uses `FakeLlm` when `CUSTODIA_ENV=local`, `AnthropicLlm` otherwise.
- [ ] `POST /api/v1/intake/{patient_id}/answer` returns `AgentAnswer` as JSON.
- [ ] 404 is returned for unknown patients.
- [ ] 400 is returned for blank questions.
- [ ] All existing unit tests still pass (`uv run pytest tests/unit/`).
- [ ] New unit tests for the route pass without an API key.
- [ ] `uv run ruff check .` and `uv run mypy .` pass with no new errors.
- [ ] `server/.env.example` documents the new settings.

---

## What Not To Do

Do not:

- Modify `IntakeAgentService`, `DefaultAgentGuardrails`, or any domain type.
- Add real Postgres (Phase 2).
- Add real Keycloak JWT validation (Phase 2).
- Add real vector search / embeddings (Phase 3).
- Add streaming responses.
- Add LangChain or LangGraph.
- Add clinical logic of any kind.
- Hardcode the API key anywhere.
- Put business logic in the route handler.

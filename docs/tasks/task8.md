Task: Add Intake Agent API endpoint

Context:
Phase 1.1 defined PatientAdministrativeProfile.
Phase 1.2 added PromptTemplate + InMemoryPromptCatalog.
The IntakeAgentService already works and is wired in runtime.
Now expose it through a thin FastAPI route.

Goal:
Add an API endpoint that allows asking an administrative intake question for a patient.

Endpoint:
POST /api/v1/intake/{patient_id}/answer

Request body:
{
  "question": "What is missing before this patient can be scheduled?"
}

Response body:
{
  "answer": "...",
  "suggested_actions": [
    {
      "description": "...",
      "requires_human_review": false
    }
  ],
  "requires_human_review": true,
  "source_references": ["..."],
  "is_ai_assisted": true
}

Scope:
- Add request/response schemas for the API layer.
- Route must be thin.
- Route should get runtime from app.state.runtime.
- Route should use current fake auth/principal from runtime.
- Route delegates to runtime.intake_agent.answer_question(...).
- Do not add real Keycloak auth yet.
- Do not add Anthropic yet.
- Do not add database persistence.
- Do not add frontend.
- Do not add cache.
- Do not add routing/orchestration yet.

Error handling:
- If PatientNotFoundError is raised, return HTTP 404.
- Keep error response simple.
- Do not expose stack traces.

Suggested files:
- server/src/custodia/interfaces/api/intake_routes.py
- server/src/custodia/interfaces/api/routes.py
- server/src/custodia/interfaces/api/schemas.py if schemas are centralized
- server/tests/unit/test_intake_api.py or tests/integration/test_intake_api.py

Testing:
- Add API test for known patient:
  POST /api/v1/intake/PAT-001/answer
  assert status 200
  assert response includes answer
  assert suggested_actions includes "Insurance verification" if PAT-001 has that missing
  assert requires_human_review is true
  assert is_ai_assisted is true

- Add API test for unknown patient:
  POST /api/v1/intake/UNKNOWN/answer
  assert status 404

- Add API test that route remains thin if practical, or at least does not directly access repositories/LLM.

Acceptance criteria:
- make server-check passes
- pytest passes
- ruff passes
- mypy passes
- no real network calls
- no real LLM calls
- no new external dependencies
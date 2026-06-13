Task: Add PromptTemplate and PromptCatalog foundation

Context:
Phase 1.1 defined the PatientAdministrativeProfile model and cleaned up IntakeAgentService.
The next step is to stop hardcoding prompt text inside IntakeAgentService.

Goal:
Introduce prompt management as a small application/domain concept without adding external services.

Scope:
- Add PromptTemplate model.
- Add PromptCatalog port.
- Add InMemoryPromptCatalog adapter.
- Update IntakeAgentService to retrieve the intake prompt from PromptCatalog.
- Keep FakeLlm.
- Do not add Anthropic yet.
- Do not add cachetools yet.
- Do not add AWS Prompt Manager yet.
- Do not add API routes yet.

Suggested files:
- server/src/custodia/domain/prompts.py
- server/src/custodia/application/ports.py
- server/src/custodia/infrastructure/prompts/in_memory_prompt_catalog.py
- server/src/custodia/application/intake_agent.py
- server/src/custodia/app/runtime.py
- tests/unit/

Model:

PromptTemplate:
- key: str
- version: str
- system_prompt: str
- user_template: str

PromptCatalog port:
- get_prompt(prompt_key: str) -> PromptTemplate

InMemoryPromptCatalog:
- contains at least one prompt:
  intake.answer_question

Prompt content:
- system prompt should say this is an administrative assistant for mental health operations.
- It must clearly say no clinical advice, no diagnosis, no treatment recommendations.
- user template should include:
  - question
  - patient display name
  - missing document labels
  - pending review document labels
  - policy context

IntakeAgentService changes:
- Inject prompt_catalog: PromptCatalog
- Replace hardcoded _build_prompt text with prompt template rendering.
- Keep prompt rendering simple for now using str.format(...)
- Keep deterministic logic unchanged.
- Keep guardrails unchanged.
- Keep audit unchanged.

Naming:
- Use explicit names:
  - prompt_catalog
  - prompt_template
  - rendered_user_prompt
  - policy_context
  - missing_document_labels
  - pending_review_document_labels

Tests:
- Add unit test for InMemoryPromptCatalog returning intake.answer_question.
- Update IntakeAgentService tests to use the prompt catalog.
- Add a test that verifies the generated prompt includes missing document labels and pending review labels.
- Existing tests must continue passing.

Acceptance criteria:
- make server-check passes
- pytest passes
- ruff passes
- mypy passes
- no external dependencies
- no real LLM calls
- no API route work
Task: Close Phase 0 documentation cleanup

Context:
Deep reviewed Phase 0 and returned PASS with minor WARNs. The codebase is ready for Phase 1, but a few documentation/spec mismatches remain.

Required changes:

1. Add server/README.md

Create server/README.md with:
- project purpose: Custodia backend
- local setup commands:
  uv sync
  uv run pytest
  uv run ruff check .
  uv run mypy .
- root shortcut:
  make server-check
- local API command if currently supported
- note that all current repositories/LLM/auth are fake/local only
- note that no real PHI should be used

2. Update task2.md or Phase 0 task documentation

Update the Phase 0 task document so it matches the actual accepted Phase 0 scope.

Specifically:
- Document that Phase 0 includes fake/scaffolded IntakeAgentService, PolicyAgentService, and DailyBriefingService as foundation sketches.
- Make clear these are fake/local implementations only and not production-ready features.
- Remove or revise the old instruction saying "Do not implement the Intake Agent yet" if it conflicts with the accepted codebase.

3. Resolve role mismatch in documentation

Do not change Keycloak realm or domain/identity.py in this task.

Instead, update the task documentation to say Phase 0 uses a simplified role model:
- admin
- clinician
- staff
- system

Mention that more granular operational roles may be introduced later.

4. Verify naming cleanup

Confirm intake_agent.py already uses explicit names:
- patient_profile_loader
- policy_context_retriever
- text_generator
- audit_recorder
- agent_guardrail

If not, rename them. If already done, no code change needed.

Acceptance criteria:
- make server-check passes
- server/README.md exists
- task2.md or equivalent Phase 0 task doc matches the actual codebase
- no Keycloak/domain role changes
- no new features
- no external dependencies
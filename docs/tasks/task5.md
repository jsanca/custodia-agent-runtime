Task: Clean up document naming and suggested action construction

Context:
AdministrativeDocument no longer has a free-form name field. It now uses document_type: AdministrativeDocumentType.
The current helper names missing_document_names() and pending_review_document_names() may be semantically inaccurate.

Scope:
- Domain and IntakeAgentService only.
- No API routes.
- No Anthropic integration.
- No prompt catalog yet.
- No persistence changes unless required by renames.
- No new external dependencies.

Required changes:

1. Rename document helper methods

Change:
- PatientAdministrativeProfile.missing_document_names()
- PatientAdministrativeProfile.pending_review_document_names()

To one of these, preferably:

- missing_document_labels()
- pending_review_document_labels()

2. Add human-readable labels to AdministrativeDocumentType

Example:
- CONSENT_FORM -> "Consent form"
- INSURANCE_VERIFICATION -> "Insurance verification"

Use either a property or method, for example:

@property
def label(self) -> str:
    ...

3. Update IntakeAgentService

Replace:

missing_document_names = patient_profile.missing_document_names()
pending_review_document_names = patient_profile.pending_review_document_names()

With:

missing_document_labels = patient_profile.missing_document_labels()
pending_review_document_labels = patient_profile.pending_review_document_labels()

4. Move deterministic action construction before LLM generation

The suggested actions and requires_review values depend only on the patient administrative state.
Compute them before retrieving policy context and before calling the text generator.

Preferred flow:

- load patient profile
- audit profile viewed
- compute missing/pending labels
- compute requires_review
- build suggested_actions
- retrieve policy context
- build prompt
- call text generator
- build AgentAnswer
- apply guardrail
- audit answered
- return guarded answer

5. Extract suggested action construction

Add a small private helper in IntakeAgentService:

_build_suggested_actions(
    missing_document_labels: tuple[str, ...],
) -> tuple[SuggestedAction, ...]

Rules:
- If no missing documents, return empty tuple.
- If missing documents exist, return a SuggestedAction asking staff to collect those documents.
- Keep explicit names. Avoid d, doc, raw, res.

6. Update tests

Update existing tests for the renamed helper methods and labels.

Acceptance criteria:
- make server-check passes
- pytest passes
- ruff passes
- mypy passes
- no behavior expansion
- no API work
- no LLM provider work
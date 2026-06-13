Task: Define patient administrative profile model

Create or refine the domain model for patient administrative intake state.

Scope:
- Work only in the domain layer unless tests require imports.
- Do not add API routes.
- Do not add LLM code.
- Do not add persistence.
- Do not add real clinical fields.

Model:
- PatientAdministrativeProfile
- AdministrativeDocument
- AdministrativeDocumentType
- IntakeStatus

PatientAdministrativeProfile should expose readable domain methods:
- missing_document_names() -> tuple[str, ...]
- pending_review_document_names() -> tuple[str, ...]
- is_ready_for_scheduling() -> bool

Rules:
- A profile is ready for scheduling only when there are no missing documents and no pending-review documents.
- The model must represent administrative status only.
- Avoid clinical data fields.

Naming:
- Prefer explicit names:
  - patient_profile
  - administrative_document
  - missing_document_names
  - pending_review_document_names
- Avoid terse names like d, doc, profile if a clearer name is available.

Testing:
- Add unit tests for:
  - profile with missing documents
  - profile with pending-review documents
  - profile ready for scheduling
  - empty document list behavior

Acceptance criteria:
- make server-check passes
- pytest passes
- ruff passes
- mypy passes
- no external dependencies added
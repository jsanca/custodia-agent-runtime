from custodia.app.runtime import build_runtime
from custodia.domain.identity import Principal, Role
from custodia.infrastructure.llm.fake_llm import FakeLlm
from custodia.infrastructure.prompts.in_memory_prompt_catalog import InMemoryPromptCatalog


def test_in_memory_prompt_catalog_returns_intake_answer_question() -> None:
    prompt_catalog = InMemoryPromptCatalog()
    prompt_template = prompt_catalog.get_prompt("intake.answer_question")

    assert prompt_template.key == "intake.answer_question"
    assert len(prompt_template.system_prompt) > 0
    assert len(prompt_template.user_template) > 0


def test_intake_prompt_system_prompt_forbids_clinical_advice() -> None:
    prompt_catalog = InMemoryPromptCatalog()
    prompt_template = prompt_catalog.get_prompt("intake.answer_question")

    system_prompt_lower = prompt_template.system_prompt.lower()
    assert "clinical" in system_prompt_lower
    assert "diagnos" in system_prompt_lower


def test_in_memory_prompt_catalog_raises_for_unknown_key() -> None:
    prompt_catalog = InMemoryPromptCatalog()
    try:
        prompt_catalog.get_prompt("unknown.key")
        assert False, "Expected KeyError"
    except KeyError:
        pass


def _make_principal() -> Principal:
    return Principal(
        subject="test-subject",
        email="test@example.com",
        roles=frozenset([Role.STAFF]),
    )


def test_rendered_prompt_includes_missing_document_labels() -> None:
    runtime = build_runtime()
    # PAT-001 has insurance_verification MISSING → label "Insurance verification"
    runtime.intake_agent.answer_question(
        principal=_make_principal(),
        patient_id="PAT-001",
        question="What documents are missing?",
    )

    text_generator = runtime.intake_agent._text_generator
    assert isinstance(text_generator, FakeLlm)
    assert text_generator.last_prompt is not None
    assert "Insurance verification" in text_generator.last_prompt


def test_rendered_prompt_includes_pending_review_document_labels() -> None:
    runtime = build_runtime()
    # PAT-002 has consent_form PENDING_REVIEW → label "Consent form"
    runtime.intake_agent.answer_question(
        principal=_make_principal(),
        patient_id="PAT-002",
        question="What is pending review?",
    )

    text_generator = runtime.intake_agent._text_generator
    assert isinstance(text_generator, FakeLlm)
    assert text_generator.last_prompt is not None
    assert "Consent form" in text_generator.last_prompt

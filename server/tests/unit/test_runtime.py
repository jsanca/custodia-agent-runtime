import pytest
from httpx import ASGITransport, AsyncClient

from custodia.app.main import create_app
from custodia.app.runtime import build_runtime
from custodia.application.intake_agent import PatientNotFoundError
from custodia.domain.agents import SuggestedAction
from custodia.domain.identity import Principal, Role


def test_build_runtime_returns_valid_runtime() -> None:
    runtime = build_runtime()
    assert runtime.settings.service_name == "custodia-server"
    assert runtime.intake_agent is not None
    assert runtime.policy_agent is not None
    assert runtime.daily_briefing is not None


@pytest.mark.asyncio
async def test_health_endpoint_returns_ok() -> None:
    runtime = build_runtime()
    app = create_app(runtime=runtime)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "custodia-server"}


@pytest.mark.asyncio
async def test_health_response_includes_request_id_header() -> None:
    runtime = build_runtime()
    app = create_app(runtime=runtime)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert "x-request-id" in response.headers


def test_intake_agent_raises_for_unknown_patient() -> None:
    runtime = build_runtime()
    principal = Principal(
        subject="test-subject",
        email="test@example.com",
        roles=frozenset([Role.STAFF]),
    )
    with pytest.raises(PatientNotFoundError):
        runtime.intake_agent.answer_question(
            principal=principal,
            patient_id="PAT-UNKNOWN",
            question="What is missing?",
        )


def test_intake_agent_answers_for_known_patient() -> None:
    runtime = build_runtime()
    principal = Principal(
        subject="test-subject",
        email="test@example.com",
        roles=frozenset([Role.STAFF]),
    )
    answer = runtime.intake_agent.answer_question(
        principal=principal,
        patient_id="PAT-002",
        question="What is missing for this patient?",
    )
    assert answer.is_ai_assisted is True
    assert len(answer.answer) > 0


def test_intake_agent_always_calls_llm_even_when_documents_are_missing() -> None:
    runtime = build_runtime()
    principal = Principal(
        subject="test-subject",
        email="test@example.com",
        roles=frozenset([Role.STAFF]),
    )
    answer = runtime.intake_agent.answer_question(
        principal=principal,
        patient_id="PAT-001",
        question="What is missing for this patient?",
    )

    assert answer.is_ai_assisted is True
    assert answer.requires_human_review is True
    assert answer.suggested_actions == (
        SuggestedAction(
            description="Collect missing documents: Insurance verification",
            requires_human_review=False,
        ),
    )

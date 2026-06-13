import pytest
from httpx import ASGITransport, AsyncClient

from custodia.app.main import create_app
from custodia.app.runtime import build_runtime


@pytest.mark.asyncio
async def test_intake_answer_returns_200_for_known_patient() -> None:
    app = create_app(runtime=build_runtime())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/intake/PAT-001/answer",
            json={"question": "What is missing before this patient can be scheduled?"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["answer"]) > 0
    assert payload["is_ai_assisted"] is True
    assert payload["requires_human_review"] is True
    descriptions = [action["description"] for action in payload["suggested_actions"]]
    assert any("Insurance verification" in description for description in descriptions)


@pytest.mark.asyncio
async def test_intake_answer_returns_404_for_unknown_patient() -> None:
    app = create_app(runtime=build_runtime())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/intake/PAT-UNKNOWN/answer",
            json={"question": "What is missing?"},
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_intake_route_delegates_to_agent_not_repository() -> None:
    runtime = build_runtime()
    app = create_app(runtime=runtime)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/intake/PAT-002/answer",
            json={"question": "What is pending review?"},
        )

    assert response.status_code == 200
    payload = response.json()
    # PAT-002 has no missing docs → no requires_human_review from missing docs
    assert payload["is_ai_assisted"] is True
    assert payload["requires_human_review"] is False

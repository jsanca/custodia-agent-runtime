from fastapi import APIRouter, HTTPException, Request

from custodia.application.intake_agent import PatientNotFoundError
from custodia.interfaces.api.schemas import (
    IntakeAnswerRequest,
    IntakeAnswerResponse,
    SuggestedActionResponse,
)

intake_router = APIRouter(prefix="/api/v1")


@intake_router.post("/intake/{patient_id}/answer", response_model=IntakeAnswerResponse)
async def answer_intake_question(
    patient_id: str,
    body: IntakeAnswerRequest,
    request: Request,
) -> IntakeAnswerResponse:
    runtime = request.app.state.runtime
    try:
        agent_answer = runtime.intake_agent.answer_question(
            principal=runtime.auth.load(),
            patient_id=patient_id,
            question=body.question,
        )
    except PatientNotFoundError:
        raise HTTPException(status_code=404, detail="Patient not found")

    return IntakeAnswerResponse(
        answer=agent_answer.answer,
        suggested_actions=[
            SuggestedActionResponse(
                description=suggested_action.description,
                requires_human_review=suggested_action.requires_human_review,
            )
            for suggested_action in agent_answer.suggested_actions
        ],
        requires_human_review=agent_answer.requires_human_review,
        source_references=list(agent_answer.source_references),
        is_ai_assisted=agent_answer.is_ai_assisted,
    )

from pydantic import BaseModel


class IntakeAnswerRequest(BaseModel):
    question: str


class SuggestedActionResponse(BaseModel):
    description: str
    requires_human_review: bool


class IntakeAnswerResponse(BaseModel):
    answer: str
    suggested_actions: list[SuggestedActionResponse]
    requires_human_review: bool
    source_references: list[str]
    is_ai_assisted: bool

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    service_name: str = request.app.state.runtime.settings.service_name
    return HealthResponse(status="ok", service=service_name)

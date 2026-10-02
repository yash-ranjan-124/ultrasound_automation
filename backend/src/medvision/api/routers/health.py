from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")


class HealthResponse(BaseModel):
    status: str
    service: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="medvision-api")

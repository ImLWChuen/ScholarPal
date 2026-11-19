from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


router = APIRouter()


@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse()

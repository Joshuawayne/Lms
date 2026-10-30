"""Separate process liveness from database readiness."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app import __version__
from app.api.dependencies import get_database_probe
from app.api.problem_details import ApiProblem, ProblemDetails
from app.shared.application.database_probe import DatabaseProbe

router = APIRouter(prefix="/health", tags=["Health"])


class LivenessResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["jjenga-lms-api"] = "jjenga-lms-api"
    version: str = __version__


class ReadinessResponse(BaseModel):
    status: Literal["ready"] = "ready"


@router.get("/live", operation_id="getLiveness")
async def get_liveness() -> LivenessResponse:
    return LivenessResponse()


@router.get(
    "/ready",
    operation_id="getReadiness",
    responses={
        503: {
            "description": "Database unavailable or unconfigured",
            "content": {"application/problem+json": {"schema": ProblemDetails.model_json_schema()}},
        }
    },
)
async def get_readiness(
    probe: Annotated[DatabaseProbe | None, Depends(get_database_probe)],
) -> ReadinessResponse:
    if probe is None:
        raise ApiProblem(
            status=503,
            title="Service Unavailable",
            detail="Database connectivity has not been configured.",
        )
    if not await probe.ping():
        raise ApiProblem(
            status=503,
            title="Service Unavailable",
            detail="The database is currently unavailable.",
        )
    return ReadinessResponse()

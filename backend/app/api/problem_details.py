"""HTTP problem details without request bodies or infrastructure secrets."""

from collections.abc import Mapping
from typing import Any

from fastapi import Request
from pydantic import BaseModel
from starlette.responses import JSONResponse


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str
    request_id: str
    errors: list[dict[str, Any]] | None = None


class ApiProblem(Exception):
    def __init__(self, *, status: int, title: str, detail: str) -> None:
        self.status = status
        self.title = title
        self.detail = detail


def problem_response(
    request: Request,
    *,
    status: int,
    title: str,
    detail: str,
    errors: list[dict[str, Any]] | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unavailable")
    problem = ProblemDetails(
        title=title,
        status=status,
        detail=detail,
        instance=request.url.path,
        request_id=request_id,
        errors=errors,
    )
    return JSONResponse(
        status_code=status,
        media_type="application/problem+json",
        content=problem.model_dump(exclude_none=True),
        headers={**(headers or {}), "X-Request-ID": request_id},
    )

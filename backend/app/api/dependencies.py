"""Resolve request-scoped application dependencies."""

from typing import cast

from fastapi import Request

from app.api.problem_details import ApiProblem
from app.modules.programs.application.ports import (
    ApplicationRepository,
    ProgramRepository,
)
from app.shared.application.database_probe import DatabaseProbe


def get_database_probe(request: Request) -> DatabaseProbe | None:
    return cast(DatabaseProbe | None, getattr(request.app.state, "database_probe", None))


def get_program_repository(request: Request) -> ProgramRepository:
    repo = getattr(request.app.state, "program_repository", None)
    if repo is None:
        raise ApiProblem(
            status=503,
            title="Service Unavailable",
            detail="Program repository is not configured.",
        )
    return cast(ProgramRepository, repo)


def get_application_repository(request: Request) -> ApplicationRepository:
    repo = getattr(request.app.state, "application_repository", None)
    if repo is None:
        raise ApiProblem(
            status=503,
            title="Service Unavailable",
            detail="Application repository is not configured.",
        )
    return cast(ApplicationRepository, repo)

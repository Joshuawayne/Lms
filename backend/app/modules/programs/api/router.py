"""API endpoints for published programs catalogue and enrolment applications."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import (
    get_application_repository,
    get_program_repository,
)
from app.api.problem_details import ApiProblem
from app.modules.programs.api.schemas import (
    ApplicationReceiptResponse,
    ProgramDetailResponse,
    ProgramListResponse,
    ProgramSummaryResponse,
    SubmitApplicationRequest,
)
from app.modules.programs.application.commands import (
    SubmitApplicationCommand,
    SubmitApplicationUseCase,
)
from app.modules.programs.application.errors import (
    ApplicationsClosedError,
    DeclarationRequiredError,
    IdempotencyConflictError,
    LearnerIneligibleError,
    ProgramNotFoundError,
)
from app.modules.programs.application.ports import (
    ApplicationRepository,
    ProgramRepository,
)
from app.modules.programs.application.queries import (
    GetPublishedProgramUseCase,
    ListPublishedProgramsQuery,
    ListPublishedProgramsUseCase,
)
from app.modules.programs.domain.values import Pathway

router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("")
async def list_programs(
    program_repo: Annotated[
        ProgramRepository,
        Depends(get_program_repository),
    ],
    pathway: Annotated[
        Pathway | None,
        Query(description="Filter by learning pathway"),
    ] = None,
    page: Annotated[
        int,
        Query(ge=1, description="Page number for pagination"),
    ] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=50, description="Items per page (max 50)"),
    ] = 12,
) -> ProgramListResponse:
    """Browse the catalogue of published learning programs."""
    use_case = ListPublishedProgramsUseCase(program_repo)
    result = await use_case.execute(
        ListPublishedProgramsQuery(pathway=pathway, page=page, page_size=page_size)
    )
    return ProgramListResponse(
        items=[ProgramSummaryResponse.from_domain(p) for p in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get(
    "/{slug}",
    responses={
        404: {"description": "No published program has this slug"},
        503: {
            "description": "Persistence temporarily unavailable; retry rather than assume absence",
        },
    },
)
async def get_program(
    slug: str,
    program_repo: Annotated[
        ProgramRepository,
        Depends(get_program_repository),
    ],
) -> ProgramDetailResponse:
    """Fetch complete details of a published program by its unique URL slug."""
    use_case = GetPublishedProgramUseCase(program_repo)
    try:
        program = await use_case.execute(slug)
    except ProgramNotFoundError as err:
        raise ApiProblem(
            status=status.HTTP_404_NOT_FOUND,
            title="Program Not Found",
            detail=err.message,
        ) from err
    return ProgramDetailResponse.from_domain(program)


@router.post(
    "/{slug}/applications",
    status_code=status.HTTP_201_CREATED,
    responses={
        200: {
            "description": "Original receipt returned for safe idempotent replay",
            "model": ApplicationReceiptResponse,
        },
        404: {"description": "Program not found or not published"},
        409: {"description": "Idempotency key reused with different request payload"},
        413: {"description": "Request body exceeds the configured size limit"},
        422: {"description": "Validation failure, ineligible age or applications closed"},
        429: {"description": "Too many submissions from this connection; see Retry-After"},
        503: {
            "description": "Persistence temporarily unavailable; the submission may need a retry",
        },
    },
)
async def submit_application(
    slug: str,
    payload: SubmitApplicationRequest,
    response: Response,
    program_repo: Annotated[
        ProgramRepository,
        Depends(get_program_repository),
    ],
    application_repo: Annotated[
        ApplicationRepository,
        Depends(get_application_repository),
    ],
) -> ApplicationReceiptResponse:
    """Submit an unverified enrolment application for a published program."""
    command = SubmitApplicationCommand(
        idempotency_key=payload.idempotency_key,
        program_slug=slug,
        guardian_name=payload.guardian_name,
        guardian_email=payload.guardian_email,
        guardian_phone=payload.guardian_phone,
        guardian_relationship=payload.guardian_relationship,
        learner_name=payload.learner_name,
        learner_age_years=payload.learner_age_years,
        notes=payload.notes,
        declaration_accepted=payload.declaration_accepted,
        declaration_version=payload.declaration_version,
    )

    use_case = SubmitApplicationUseCase(program_repo, application_repo)
    try:
        result = await use_case.execute(command)
    except ProgramNotFoundError as err:
        raise ApiProblem(
            status=status.HTTP_404_NOT_FOUND,
            title="Program Not Found",
            detail=err.message,
        ) from err
    except IdempotencyConflictError as err:
        raise ApiProblem(
            status=status.HTTP_409_CONFLICT,
            title="Idempotency Conflict",
            detail=err.message,
        ) from err
    except ApplicationsClosedError as err:
        raise ApiProblem(
            status=status.HTTP_422_UNPROCESSABLE_CONTENT,
            title="Applications Closed",
            detail=err.message,
        ) from err
    except LearnerIneligibleError as err:
        raise ApiProblem(
            status=status.HTTP_422_UNPROCESSABLE_CONTENT,
            title="Learner Ineligible",
            detail=err.message,
        ) from err
    except DeclarationRequiredError as err:
        raise ApiProblem(
            status=status.HTTP_422_UNPROCESSABLE_CONTENT,
            title="Declaration Required",
            detail=err.message,
        ) from err

    if result.is_retry:
        response.status_code = status.HTTP_200_OK

    return ApplicationReceiptResponse(
        id=result.record.id,
        reference=result.record.reference,
        program_id=result.record.program_id,
        status=result.record.status,
        submitted_at=result.record.submitted_at,
        is_retry=result.is_retry,
    )

"""Composition root: connect framework adapters and application capabilities."""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app import __version__
from app.api.middleware.exception_handler import ExceptionHandlerMiddleware
from app.api.middleware.request_context import RequestContextMiddleware
from app.api.middleware.submission_protection import SubmissionProtectionMiddleware
from app.api.problem_details import ApiProblem, ProblemDetails, problem_response
from app.api.v1.router import router
from app.config import Settings
from app.infrastructure.database.connection import PostgresProbe, create_connection_factory
from app.modules.programs.application.errors import ProgramServiceUnavailableError
from app.modules.programs.application.ports import (
    ApplicationRepository,
    ProgramRepository,
)
from app.modules.programs.infrastructure.postgres import (
    PostgresApplicationRepository,
    PostgresProgramRepository,
)
from app.shared.application.database_probe import DatabaseProbe


def create_app(
    settings: Settings | None = None,
    database_probe: DatabaseProbe | None = None,
    program_repository: ProgramRepository | None = None,
    application_repository: ApplicationRepository | None = None,
) -> FastAPI:
    settings = settings if settings is not None else Settings()
    if settings.database_url is not None:
        if database_probe is None:
            database_probe = PostgresProbe(settings.database_url, settings.database_sslrootcert)
        if program_repository is None:
            factory = create_connection_factory(
                settings.database_url, settings.database_sslrootcert
            )
            program_repository = PostgresProgramRepository(factory)
        if application_repository is None:
            factory = create_connection_factory(
                settings.database_url, settings.database_sslrootcert
            )
            application_repository = PostgresApplicationRepository(factory)

    app = FastAPI(
        title="Jjenga Code LMS API",
        version=__version__,
        description="Core catalogue, programs and enrolment applications.",
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
        debug=False,
        responses={
            status: {
                "description": HTTPStatus(status).phrase,
                "content": {
                    "application/problem+json": {"schema": ProblemDetails.model_json_schema()}
                },
            }
            for status in [404, 422, 500]
        },
    )
    app.state.database_probe = database_probe
    app.state.program_repository = program_repository
    app.state.application_repository = application_repository

    @app.exception_handler(ApiProblem)
    async def handle_problem(request: Request, error: ApiProblem) -> JSONResponse:
        return problem_response(
            request, status=error.status, title=error.title, detail=error.detail
        )

    @app.exception_handler(ProgramServiceUnavailableError)
    async def handle_unavailable(
        request: Request, error: ProgramServiceUnavailableError
    ) -> JSONResponse:
        # A retryable outage, deliberately distinct from 404 so clients never treat
        # "the database is down" as "this program does not exist".
        return problem_response(
            request,
            status=503,
            title="Service Unavailable",
            detail=error.message,
            headers={"Retry-After": "5"},
        )

    @app.exception_handler(HTTPException)
    async def handle_http_error(request: Request, error: HTTPException) -> JSONResponse:
        return problem_response(
            request,
            status=error.status_code,
            title=HTTPStatus(error.status_code).phrase,
            detail=error.detail if isinstance(error.detail, str) else "The request failed.",
            headers=error.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_invalid_request(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        return problem_response(
            request,
            status=422,
            title="Unprocessable Content",
            detail="Check the request fields and try again.",
            errors=[
                {"location": list(item["loc"]), "code": item["type"], "message": item["msg"]}
                for item in error.errors()
            ],
        )

    app.include_router(router)

    # In FastAPI / Starlette, middleware is executed in reverse order of addition.
    # CORSMiddleware is added last so it becomes the outermost layer, ensuring
    # preflights are handled and CORS headers are attached to all responses
    # (including error responses produced by inner middleware).  The submission
    # protection sits innermost so its 413/429 problems carry a request ID and CORS.
    app.add_middleware(
        SubmissionProtectionMiddleware,
        max_body_bytes=settings.max_request_body_bytes,
        rate_limit=settings.submission_rate_limit,
        window_seconds=settings.submission_rate_window_seconds,
    )
    app.add_middleware(ExceptionHandlerMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Accept", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    return app

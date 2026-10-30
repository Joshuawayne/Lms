"""Application use cases and ports for the programs module.

Use cases coordinate business workflows. They depend on domain rules
and repository contracts (ports), not on concrete database adapters.
"""

from app.modules.programs.application.commands import (
    CURRENT_DECLARATION_VERSION,
    SubmitApplicationCommand,
    SubmitApplicationResult,
    SubmitApplicationUseCase,
    compute_payload_fingerprint,
    generate_reference,
)
from app.modules.programs.application.errors import (
    ApplicationsClosedError,
    DeclarationRequiredError,
    IdempotencyConflictError,
    LearnerIneligibleError,
    ProgramError,
    ProgramNotFoundError,
)
from app.modules.programs.application.ports import (
    ApplicationReplayRecord,
    ApplicationRepository,
    ApplicationSubmission,
    ProgramRepository,
    SubmissionResult,
)
from app.modules.programs.application.queries import (
    GetPublishedProgramUseCase,
    ListPublishedProgramsQuery,
    ListPublishedProgramsUseCase,
    PaginatedProgramsResult,
)

__all__ = [
    "CURRENT_DECLARATION_VERSION",
    "ApplicationReplayRecord",
    "ApplicationRepository",
    "ApplicationSubmission",
    "ApplicationsClosedError",
    "DeclarationRequiredError",
    "GetPublishedProgramUseCase",
    "IdempotencyConflictError",
    "LearnerIneligibleError",
    "ListPublishedProgramsQuery",
    "ListPublishedProgramsUseCase",
    "PaginatedProgramsResult",
    "ProgramError",
    "ProgramNotFoundError",
    "ProgramRepository",
    "SubmissionResult",
    "SubmitApplicationCommand",
    "SubmitApplicationResult",
    "SubmitApplicationUseCase",
    "compute_payload_fingerprint",
    "generate_reference",
]

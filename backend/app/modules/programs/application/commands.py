"""Command use cases for the programs module, including application submissions."""

from __future__ import annotations

import hashlib
import json
import secrets
import uuid
from dataclasses import dataclass

from app.modules.programs.application.errors import (
    ApplicationsClosedError,
    DeclarationRequiredError,
    IdempotencyConflictError,
    LearnerIneligibleError,
    ProgramNotFoundError,
)
from app.modules.programs.application.ports import (
    ApplicationReplayRecord,
    ApplicationRepository,
    ApplicationSubmission,
    ProgramRepository,
)
from app.modules.programs.domain.values import GuardianRelationship

CURRENT_DECLARATION_VERSION = 1


def compute_payload_fingerprint(
    *,
    program_id: uuid.UUID,
    guardian_name: str,
    guardian_email: str,
    guardian_phone: str | None,
    guardian_relationship: GuardianRelationship,
    learner_name: str,
    learner_age_years: int,
    notes: str | None,
    declaration_version: int,
) -> str:
    """Compute a canonical SHA-256 hex digest for an application payload.

    Used to detect safe idempotent replays (identical payload) versus
    conflicting reuses of the same idempotency key (different payload).
    """
    canonical_data = {
        "declaration_version": declaration_version,
        "guardian_email": guardian_email.strip().lower(),
        "guardian_name": guardian_name.strip(),
        "guardian_phone": guardian_phone.strip() if guardian_phone else None,
        "guardian_relationship": guardian_relationship.value,
        "learner_age_years": learner_age_years,
        "learner_name": learner_name.strip(),
        "notes": notes.strip() if notes else None,
        "program_id": str(program_id),
    }
    encoded = json.dumps(canonical_data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def generate_reference(prefix: str = "JC") -> str:
    """Generate a friendly, unique application reference (e.g. JC-20261028-A4F19B)."""
    random_part = secrets.token_hex(3).upper()
    return f"{prefix}-{secrets.token_hex(2).upper()}-{random_part}"


@dataclass(frozen=True)
class SubmitApplicationCommand:
    """User input for submitting an enrolment application."""

    idempotency_key: uuid.UUID
    program_slug: str
    guardian_name: str
    guardian_email: str
    guardian_phone: str | None
    guardian_relationship: GuardianRelationship
    learner_name: str
    learner_age_years: int
    notes: str | None
    declaration_accepted: bool
    declaration_version: int = CURRENT_DECLARATION_VERSION


@dataclass(frozen=True)
class SubmitApplicationResult:
    """Result of an application submission or idempotent replay."""

    record: ApplicationReplayRecord
    is_retry: bool


class SubmitApplicationUseCase:
    """Validate and persist an enrolment application idempotently."""

    def __init__(
        self,
        program_repo: ProgramRepository,
        application_repo: ApplicationRepository,
    ) -> None:
        self._program_repo = program_repo
        self._application_repo = application_repo

    async def execute(self, command: SubmitApplicationCommand) -> SubmitApplicationResult:
        # 1. Resolve program by slug.
        program = await self._program_repo.get_by_slug(command.program_slug)
        if program is None:
            raise ProgramNotFoundError(command.program_slug)

        # 2. Compute canonical request fingerprint.
        fingerprint = compute_payload_fingerprint(
            program_id=program.id,
            guardian_name=command.guardian_name,
            guardian_email=command.guardian_email,
            guardian_phone=command.guardian_phone,
            guardian_relationship=command.guardian_relationship,
            learner_name=command.learner_name,
            learner_age_years=command.learner_age_years,
            notes=command.notes,
            declaration_version=command.declaration_version,
        )

        # 3. Check for existing idempotency key before rejecting for closure.
        existing = await self._application_repo.find_by_idempotency_key(command.idempotency_key)
        if existing is not None:
            if existing.request_fingerprint == fingerprint:
                # Safe replay — return original receipt even if applications are now closed.
                return SubmitApplicationResult(record=existing, is_retry=True)
            raise IdempotencyConflictError()

        # 4. Enforce declaration agreement.
        if not command.declaration_accepted:
            raise DeclarationRequiredError(CURRENT_DECLARATION_VERSION)
        if command.declaration_version != CURRENT_DECLARATION_VERSION:
            raise DeclarationRequiredError(CURRENT_DECLARATION_VERSION)

        # 5. Preliminary helpful check against program open/close window using DB time.
        now = await self._application_repo.get_current_time()
        if not program.accepts_applications(now):
            raise ApplicationsClosedError(program.title)

        # 6. Validate program-specific age eligibility.
        if program.min_age_years is not None and command.learner_age_years < program.min_age_years:
            raise LearnerIneligibleError(
                f"Learner must be at least {program.min_age_years} years old for {program.title}."
            )
        if program.max_age_years is not None and command.learner_age_years > program.max_age_years:
            raise LearnerIneligibleError(
                f"Learner must be at most {program.max_age_years} years old for {program.title}."
            )

        # 7. Atomically insert in database with enforced availability and race handling.
        submission = ApplicationSubmission(
            idempotency_key=command.idempotency_key,
            request_fingerprint=fingerprint,
            program_id=program.id,
            guardian_name=command.guardian_name.strip(),
            guardian_email=command.guardian_email.strip().lower(),
            guardian_phone=command.guardian_phone.strip() if command.guardian_phone else None,
            guardian_relationship=command.guardian_relationship,
            learner_name=command.learner_name.strip(),
            learner_age_years=command.learner_age_years,
            notes=command.notes.strip() if command.notes else None,
            declaration_version=command.declaration_version,
            reference=generate_reference(),
        )

        result = await self._application_repo.insert_application(submission)
        return SubmitApplicationResult(record=result.record, is_retry=not result.is_new)

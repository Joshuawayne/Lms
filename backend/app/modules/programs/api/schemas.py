"""Pydantic schemas for the programs and enrolment applications HTTP contract."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.programs.domain.entities import Program
from app.modules.programs.domain.values import (
    ApplicationStatus,
    GuardianRelationship,
    Pathway,
    ProgramDelivery,
    ProgramStatus,
)


class ProgramSummaryResponse(BaseModel):
    """Brief public overview of a published program."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pathway: Pathway
    title: str
    slug: str = Field(
        ...,
        pattern=r"^[a-z0-9]([a-z0-9-]{0,98}[a-z0-9])?$",
        description="URL slug (1-100 lowercase alphanumeric characters with hyphens).",
    )
    summary: str
    delivery: ProgramDelivery
    status: ProgramStatus
    applications_enabled: bool
    applications_open_at: datetime | None
    applications_close_at: datetime | None
    starts_on: date | None
    ends_on: date | None
    max_enrolments: int | None
    min_age_years: int | None
    max_age_years: int | None
    display_order: int

    @classmethod
    def from_domain(cls, program: Program) -> ProgramSummaryResponse:
        return cls(
            id=program.id,
            pathway=program.pathway,
            title=program.title,
            slug=program.slug,
            summary=program.summary,
            delivery=program.delivery,
            status=program.status,
            applications_enabled=program.applications_enabled,
            applications_open_at=program.applications_open_at,
            applications_close_at=program.applications_close_at,
            starts_on=program.starts_on,
            ends_on=program.ends_on,
            max_enrolments=program.max_enrolments,
            min_age_years=program.min_age_years,
            max_age_years=program.max_age_years,
            display_order=program.display_order,
        )


class ProgramDetailResponse(ProgramSummaryResponse):
    """Full public details of a published program including rich description."""

    description: str

    @classmethod
    def from_domain(cls, program: Program) -> ProgramDetailResponse:
        return cls(
            id=program.id,
            pathway=program.pathway,
            title=program.title,
            slug=program.slug,
            summary=program.summary,
            description=program.description,
            delivery=program.delivery,
            status=program.status,
            applications_enabled=program.applications_enabled,
            applications_open_at=program.applications_open_at,
            applications_close_at=program.applications_close_at,
            starts_on=program.starts_on,
            ends_on=program.ends_on,
            max_enrolments=program.max_enrolments,
            min_age_years=program.min_age_years,
            max_age_years=program.max_age_years,
            display_order=program.display_order,
        )


class ProgramListResponse(BaseModel):
    """Paginated collection of published programs."""

    items: list[ProgramSummaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SubmitApplicationRequest(BaseModel):
    """Applicant payload for submitting an enrolment application.

    Unknown properties (for example a client trying to send ``status`` or
    ``reviewed_at``) are rejected rather than silently discarded.
    """

    model_config = ConfigDict(extra="forbid")

    idempotency_key: uuid.UUID = Field(
        ...,
        description="Client-generated UUID to ensure submission idempotency.",
    )
    guardian_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Full name of the parent or guardian.",
    )
    guardian_email: str = Field(
        ...,
        min_length=5,
        max_length=254,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        description="Contact email address for application correspondence.",
    )
    guardian_phone: str | None = Field(
        None,
        min_length=5,
        max_length=30,
        description="Optional contact telephone number.",
    )
    guardian_relationship: GuardianRelationship = Field(
        ...,
        description="Relationship of the applicant to the learner.",
    )
    learner_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Full name of the learner.",
    )
    learner_age_years: int = Field(
        ...,
        strict=True,
        ge=1,
        le=99,
        description=(
            "Age of the learner in completed years, as a whole number. "
            "Program eligibility is checked separately against the program's own age range."
        ),
    )
    notes: str | None = Field(
        None,
        max_length=1000,
        description="Optional additional context or special learning requirements.",
    )
    declaration_accepted: bool = Field(
        ...,
        strict=True,
        description="Must be true to acknowledge and accept the applicant declaration.",
    )
    declaration_version: int = Field(
        1,
        strict=True,
        gt=0,
        description="Positive version number of the declaration text agreed to.",
    )

    @field_validator("guardian_name", "learner_name", mode="after")
    @classmethod
    def validate_non_whitespace(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            msg = "Field cannot be empty or whitespace only."
            raise ValueError(msg)
        return trimmed

    @field_validator("guardian_phone", "notes", mode="after")
    @classmethod
    def trim_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed if trimmed else None


class ApplicationReceiptResponse(BaseModel):
    """Minimal receipt returned to the guardian after submission.

    Excludes personal data from replay-query output in accordance with
    least-privilege database permissions.
    """

    id: uuid.UUID
    reference: str = Field(
        ...,
        description="Unique, human-friendly application tracking reference.",
    )
    program_id: uuid.UUID
    status: ApplicationStatus
    submitted_at: datetime
    is_retry: bool = Field(
        ...,
        description="True if this response was returned from an earlier identical submission.",
    )

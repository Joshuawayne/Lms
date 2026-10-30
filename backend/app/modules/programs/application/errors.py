"""Application-layer domain exceptions for the programs module.

These exceptions describe business-rule violations and invariant failures
independently of HTTP or database-specific terminology. The API layer
maps these to appropriate RFC 9457 Problem Details responses.
"""

from __future__ import annotations


class ProgramError(Exception):
    """Base exception for all programs module business errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ProgramServiceUnavailableError(ProgramError):
    """Raised when persistence cannot be reached.

    Callers can retry instead of assuming absence.
    """

    def __init__(self) -> None:
        super().__init__("Program data is temporarily unavailable. Please try again shortly.")


class ProgramNotFoundError(ProgramError):
    """Raised when a requested program does not exist or is not published."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Program '{identifier}' was not found.")
        self.identifier = identifier


class ApplicationsClosedError(ProgramError):
    """Raised when an application is submitted to a program not currently accepting them."""

    def __init__(self, program_title: str, reason: str = "Applications are closed.") -> None:
        super().__init__(f"Applications for '{program_title}' are not currently accepted: {reason}")
        self.program_title = program_title
        self.reason = reason


class IdempotencyConflictError(ProgramError):
    """Raised when an idempotency key was previously used with a different request payload."""

    def __init__(self) -> None:
        super().__init__(
            "An application with this idempotency key already exists with different details."
        )


class LearnerIneligibleError(ProgramError):
    """Raised when a learner does not meet program-specific eligibility criteria (e.g. age)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class DeclarationRequiredError(ProgramError):
    """Raised when an applicant has not agreed to the required declaration version."""

    def __init__(self, expected_version: int) -> None:
        super().__init__(
            f"The applicant declaration must be accepted (version {expected_version})."
        )
        self.expected_version = expected_version

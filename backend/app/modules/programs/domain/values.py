"""Value objects shared across the programs module.

Enums and constrained types that express business vocabulary without
depending on Pydantic, FastAPI or database libraries.  Pydantic is used
here only for its serialisation-free enum support; these enums carry no
HTTP or persistence meaning.
"""

from enum import StrEnum


class Pathway(StrEnum):
    """The three learning pathway categories offered by Jjenga Code."""

    SCHOOL_TERM = "school_term"
    SATURDAY_CLUB = "saturday_club"
    HOLIDAY = "holiday"


class ProgramStatus(StrEnum):
    """Publication lifecycle of a program.

    Only 'published' programs are visible in public listings.
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ProgramDelivery(StrEnum):
    """How a program is delivered to learners."""

    IN_PERSON = "in_person"
    ONLINE = "online"
    HYBRID = "hybrid"


class ApplicationStatus(StrEnum):
    """Lifecycle of an enrolment application.

    Applications start as 'submitted' and move through review.
    An application must not automatically create an approved enrolment.
    """

    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class GuardianRelationship(StrEnum):
    """The applicant's relationship to the learner."""

    PARENT = "parent"
    GUARDIAN = "guardian"
    GRANDPARENT = "grandparent"
    SIBLING = "sibling"
    OTHER = "other"

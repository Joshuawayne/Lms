"""Infrastructure adapters for the programs module.

Includes PostgreSQL repositories targeting the 'lms' schema and
in-memory implementations for fast unit and integration testing.
"""

from app.modules.programs.infrastructure.in_memory import (
    InMemoryApplicationRepository,
    InMemoryProgramRepository,
)
from app.modules.programs.infrastructure.postgres import (
    PostgresApplicationRepository,
    PostgresProgramRepository,
)

__all__ = [
    "InMemoryApplicationRepository",
    "InMemoryProgramRepository",
    "PostgresApplicationRepository",
    "PostgresProgramRepository",
]

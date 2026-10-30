"""Query use cases for retrieving published programs from the catalogue."""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.modules.programs.application.errors import ProgramNotFoundError
from app.modules.programs.application.ports import ProgramRepository
from app.modules.programs.domain.entities import Program
from app.modules.programs.domain.values import Pathway


@dataclass(frozen=True)
class ListPublishedProgramsQuery:
    """Parameters for browsing the public program catalogue."""

    pathway: Pathway | None = None
    page: int = 1
    page_size: int = 12


@dataclass(frozen=True)
class PaginatedProgramsResult:
    """Paginated collection of published programs."""

    items: list[Program]
    total: int
    page: int
    page_size: int
    total_pages: int


class ListPublishedProgramsUseCase:
    """List published programs with optional pathway filtering and pagination."""

    def __init__(self, program_repo: ProgramRepository) -> None:
        self._program_repo = program_repo

    async def execute(self, query: ListPublishedProgramsQuery) -> PaginatedProgramsResult:
        page = max(1, query.page)
        page_size = max(1, min(50, query.page_size))

        items, total = await self._program_repo.list_published(
            pathway=query.pathway,
            page=page,
            page_size=page_size,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return PaginatedProgramsResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class GetPublishedProgramUseCase:
    """Fetch a single published program by its URL slug."""

    def __init__(self, program_repo: ProgramRepository) -> None:
        self._program_repo = program_repo

    async def execute(self, slug: str) -> Program:
        program = await self._program_repo.get_by_slug(slug)
        if program is None:
            raise ProgramNotFoundError(slug)
        return program

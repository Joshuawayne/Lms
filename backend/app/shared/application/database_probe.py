"""Minimal database capability needed by the readiness check."""

from typing import Protocol


class DatabaseProbe(Protocol):
    async def ping(self) -> bool:
        """Return whether a database connection can execute a trivial query."""
        ...

"""Runner script setting WindowsSelectorEventLoopPolicy and loop factory before Uvicorn starts."""

import asyncio
import sys

if sys.platform == "win32":
    if sys.version_info < (3, 14):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore[deprecated]
    import uvicorn.loops.asyncio

    def _selector_loop_factory(use_subprocess: bool = False) -> type[asyncio.SelectorEventLoop]:
        return asyncio.SelectorEventLoop

    uvicorn.loops.asyncio.asyncio_loop_factory = _selector_loop_factory

import uvicorn

from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, loop="asyncio")

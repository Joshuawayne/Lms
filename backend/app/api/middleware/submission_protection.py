"""Body-size and rate protection for the public application submission endpoint.

Scope and limits (be honest about what this is):
  * Applies only to ``POST /api/v1/programs/{slug}/applications``.
  * The body limit is enforced on the declared Content-Length and again on the
    bytes actually streamed, so a missing or false header cannot bypass it.
  * The rate limiter is a sliding window kept in this worker's memory, keyed by
    the immediate peer address.  With several workers or instances the effective
    limit multiplies, and behind a proxy every client shares the proxy's peer
    address.  A reverse proxy or WAF must therefore supply the authoritative
    limit; this layer is the application-level backstop.
  * CORS is a browser rule, not abuse prevention, and is not part of this.
"""

from __future__ import annotations

import re
import time
from collections import deque
from collections.abc import Callable
from http import HTTPStatus

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.api.problem_details import problem_response

_SUBMISSION_PATH = re.compile(r"^/api/v1/programs/[^/]+/applications/?$")
_MAX_TRACKED_CLIENTS = 10_000


class SubmissionProtectionMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        max_body_bytes: int,
        rate_limit: int,
        window_seconds: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.app = app
        self._max_body_bytes = max_body_bytes
        self._rate_limit = rate_limit
        self._window_seconds = window_seconds
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}

    @staticmethod
    def _is_protected(scope: Scope) -> bool:
        return scope["method"] == "POST" and bool(_SUBMISSION_PATH.match(scope["path"]))

    def _retry_after(self, client: str) -> int | None:
        """Record one attempt; return seconds to wait if the client is over its limit."""
        if self._rate_limit == 0:
            return None
        now = self._clock()
        if len(self._hits) > _MAX_TRACKED_CLIENTS:
            self._forget_idle_clients(now)
        window = self._hits.setdefault(client, deque())
        while window and now - window[0] >= self._window_seconds:
            window.popleft()
        if len(window) >= self._rate_limit:
            return max(1, int(self._window_seconds - (now - window[0])) + 1)
        window.append(now)
        return None

    def _forget_idle_clients(self, now: float) -> None:
        for client in [
            name
            for name, hits in self._hits.items()
            if not hits or now - hits[-1] >= self._window_seconds
        ]:
            del self._hits[client]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self._is_protected(scope):
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        declared = request.headers.get("content-length")
        if declared is not None and (
            not declared.isdigit() or int(declared) > self._max_body_bytes
        ):
            await self._too_large(request, scope, receive, send)
            return

        client = scope["client"][0] if scope.get("client") else "unknown"
        retry_after = self._retry_after(client)
        if retry_after is not None:
            response = problem_response(
                request,
                status=429,
                title="Too Many Requests",
                detail="Too many submissions from this connection. Please wait and try again.",
                headers={"Retry-After": str(retry_after)},
            )
            await response(scope, receive, send)
            return

        received = 0

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self._max_body_bytes:
                    # FastAPI re-raises HTTPException from body parsing, so the registered
                    # problem handler answers with 413 instead of a generic 400.
                    raise HTTPException(
                        status_code=413,
                        detail=f"The request body must not exceed {self._max_body_bytes} bytes.",
                    )
            return message

        await self.app(scope, limited_receive, send)

    async def _too_large(
        self, request: Request, scope: Scope, receive: Receive, send: Send
    ) -> None:
        response = problem_response(
            request,
            status=413,
            title=HTTPStatus(413).phrase,
            detail=f"The request body must not exceed {self._max_body_bytes} bytes.",
        )
        await response(scope, receive, send)

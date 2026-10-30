"""Convert unexpected failures before a response starts into safe HTTP problems."""

import logging

from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.api.problem_details import problem_response

logger = logging.getLogger("jjenga.api")


class ExceptionHandlerMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def track_response(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, track_response)
        except Exception as error:
            request = Request(scope)
            logger.error(
                "Unhandled request failure request_id=%s error_type=%s",
                getattr(request.state, "request_id", "unavailable"),
                type(error).__name__,
            )
            if response_started:
                raise
            response = problem_response(
                request,
                status=500,
                title="Internal Server Error",
                detail="The request could not be completed. Use the request ID when reporting it.",
            )
            await response(scope, receive, send)

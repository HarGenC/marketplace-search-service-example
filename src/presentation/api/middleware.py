import logging

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.trace import TRACE_ID_HEADER, trace_context

logger = logging.getLogger(__name__)


class TraceIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = Headers(scope=scope).get(TRACE_ID_HEADER)

        with trace_context(incoming) as trace_id:

            async def send_with_trace_id(message: Message) -> None:
                if message["type"] == "http.response.start":
                    MutableHeaders(scope=message).append(TRACE_ID_HEADER, trace_id)
                await send(message)

            try:
                await self.app(scope, receive, send_with_trace_id)
            except Exception:
                logger.exception("unhandled error")
                raise

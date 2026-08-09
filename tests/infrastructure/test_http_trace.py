import httpx

from src.infrastructure.http.trace import add_trace_id
from src.trace import trace_context


async def test_hook_sets_header_inside_context() -> None:
    request = httpx.Request("GET", "http://test/internal/ads/1")

    with trace_context("abc"):
        await add_trace_id(request)

    assert request.headers["X-Trace-Id"] == "abc"


async def test_hook_skips_header_outside_context() -> None:
    request = httpx.Request("GET", "http://test/internal/ads/1")

    await add_trace_id(request)

    assert "X-Trace-Id" not in request.headers


async def test_client_sends_trace_id() -> None:
    seen: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers.get("X-Trace-Id"))
        return httpx.Response(200)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport,
        event_hooks={"request": [add_trace_id]},
    ) as client:
        with trace_context("abc"):
            await client.get("http://test/internal/ads/1")
        await client.get("http://test/internal/ads/1")

    assert seen == ["abc", None]

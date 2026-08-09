import httpx

from src.trace import TRACE_ID_HEADER, get_trace_id


async def add_trace_id(request: httpx.Request) -> None:
    trace_id = get_trace_id()
    if trace_id:
        request.headers[TRACE_ID_HEADER] = trace_id

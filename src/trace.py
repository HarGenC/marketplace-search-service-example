import contextlib
import contextvars
import typing
import uuid

TRACE_ID_HEADER = "X-Trace-Id"
KAFKA_TRACE_ID_HEADER = "x-trace-id"

trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "trace_id", default=""
)


def get_trace_id() -> str:
    return trace_id_var.get()


def new_trace_id() -> str:
    return str(uuid.uuid4())


@contextlib.contextmanager
def trace_context(trace_id: str | None = None) -> typing.Iterator[str]:
    trace_id = trace_id or new_trace_id()
    token = trace_id_var.set(trace_id)
    try:
        yield trace_id
    finally:
        trace_id_var.reset(token)


def to_kafka_headers(trace_id: str) -> list[tuple[str, bytes]]:
    if not trace_id:
        return []
    return [(KAFKA_TRACE_ID_HEADER, trace_id.encode("utf-8"))]


def trace_id_from_kafka_headers(
    headers: typing.Sequence[tuple[str, bytes]] | None,
) -> str | None:
    for key, value in headers or ():
        if key.lower() == KAFKA_TRACE_ID_HEADER:
            return value.decode("utf-8")
    return None

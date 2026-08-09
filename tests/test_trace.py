import asyncio
import uuid

from src.trace import (
    get_trace_id,
    to_kafka_headers,
    trace_context,
    trace_id_from_kafka_headers,
)


def test_trace_id_is_empty_outside_context() -> None:
    assert get_trace_id() == ""


def test_trace_context_sets_and_restores() -> None:
    with trace_context("abc") as trace_id:
        assert trace_id == "abc"
        assert get_trace_id() == "abc"

    assert get_trace_id() == ""


def test_trace_context_generates_uuid_when_missing() -> None:
    with trace_context() as trace_id:
        uuid.UUID(trace_id)
        assert get_trace_id() == trace_id


def test_nested_trace_contexts() -> None:
    with trace_context("outer"):
        with trace_context("inner"):
            assert get_trace_id() == "inner"
        assert get_trace_id() == "outer"


async def test_parallel_tasks_do_not_share_trace_id() -> None:
    async def run(trace_id: str) -> str:
        with trace_context(trace_id):
            await asyncio.sleep(0)
            return get_trace_id()

    first, second = await asyncio.gather(run("first"), run("second"))

    assert first == "first"
    assert second == "second"


def test_kafka_headers_round_trip() -> None:
    headers = to_kafka_headers("abc")

    assert trace_id_from_kafka_headers(headers) == "abc"


def test_kafka_headers_are_case_insensitive() -> None:
    assert trace_id_from_kafka_headers([("X-Trace-Id", b"abc")]) == "abc"


def test_kafka_headers_without_trace_id() -> None:
    assert to_kafka_headers("") == []
    assert trace_id_from_kafka_headers(None) is None
    assert trace_id_from_kafka_headers([("other", b"1")]) is None

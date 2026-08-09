import logging

from src.logging_setup import LOG_FORMAT, LoggerNameFilter, TraceIdFilter
from src.trace import trace_context


def make_record() -> logging.LogRecord:
    return logging.LogRecord(
        name="src.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )


def test_filter_sets_trace_id_from_context() -> None:
    record = make_record()

    with trace_context("abc"):
        assert TraceIdFilter().filter(record) is True

    assert record.trace_id == "abc"


def test_filter_sets_placeholder_outside_context() -> None:
    record = make_record()

    assert TraceIdFilter().filter(record) is True
    assert record.trace_id == "-"


def test_log_format_renders_trace_id() -> None:
    record = make_record()

    with trace_context("abc"):
        TraceIdFilter().filter(record)

    assert "[abc]" in logging.Formatter(LOG_FORMAT).format(record)


def test_logger_name_filter_renames_uvicorn_error() -> None:
    record = make_record()
    record.name = "uvicorn.error"

    assert LoggerNameFilter().filter(record) is True
    assert record.name == "uvicorn"


def test_logger_name_filter_keeps_other_names() -> None:
    record = make_record()

    assert LoggerNameFilter().filter(record) is True
    assert record.name == "src.test"

import logging
import logging.config

from src.trace import get_trace_id

LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(trace_id)s] %(name)s: %(message)s"
LOGGER_NAME_ALIASES = {"uvicorn.error": "uvicorn"}


class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id() or "-"
        return True


class LoggerNameFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.name = LOGGER_NAME_ALIASES.get(record.name, record.name)
        return True


def setup_logging(level: str = "INFO") -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "trace_id": {"()": TraceIdFilter},
                "logger_name": {"()": LoggerNameFilter},
            },
            "formatters": {"default": {"format": LOG_FORMAT}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "filters": ["trace_id", "logger_name"],
                },
            },
            "root": {"handlers": ["console"], "level": level},
        },
    )

import json
import logging
import time
from contextlib import contextmanager
from typing import Iterator


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "event"):
            payload["event"] = record.event
        return json.dumps(payload, ensure_ascii=True)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


@contextmanager
def timed_event(logger: logging.Logger, event: str, **fields: object) -> Iterator[dict]:
    started = time.perf_counter()
    state = {"event": event, **fields}
    try:
        yield state
    finally:
        elapsed = round((time.perf_counter() - started) * 1000)
        logger.info("graph event complete", extra={"event": {**state, "duration_ms": elapsed}})

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # include extras (like inserted/source/status/etc.)
        for k, v in record.__dict__.items():
            if k in ("args", "msg", "levelname", "levelno", "name", "pathname", "filename",
                     "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
                     "created", "msecs", "relativeCreated", "thread", "threadName",
                     "processName", "process"):
                continue
            payload[k] = v

        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def setup_json_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

from __future__ import annotations

import logging
import time
from fastapi import Request

log = logging.getLogger("http")


async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        dur_ms = (time.perf_counter() - start) * 1000.0
        log.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query),
                "status": status_code,
                "duration_ms": round(dur_ms, 2),
                "client": request.client.host if request.client else None,
            },
        )

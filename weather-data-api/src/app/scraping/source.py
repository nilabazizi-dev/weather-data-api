from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import time

import httpx


@dataclass
class HtmlDocument:
    url: str
    fetched_at: datetime
    html: str


class SnapshotFileHtmlSource:
    """
    Reads HTML from a local file (NO internet).
    Used for testing and safe scraping.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def fetch(self) -> HtmlDocument:
        html_text = self.file_path.read_text(encoding="utf-8")
        return HtmlDocument(
            url=f"snapshot://{self.file_path.name}",
            fetched_at=datetime.now(timezone.utc),
            html=html_text,
        )


class HttpHtmlSource:
    """
    Fetches HTML from the real website (polite scraping):
    - custom User-Agent
    - timeout
    - simple exponential backoff retry
    """

    def __init__(
        self,
        url: str,
        user_agent: str,
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
        backoff_seconds: float = 1.0,
    ):
        self.url = url
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

    def fetch(self) -> HtmlDocument:
        headers = {"User-Agent": self.user_agent}

        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_seconds, headers=headers) as client:
                    r = client.get(self.url)
                    r.raise_for_status()
                    return HtmlDocument(
                        url=self.url,
                        fetched_at=datetime.now(timezone.utc),
                        html=r.text,
                    )
            except Exception as e:
                last_exc = e
                if attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * (2 ** (attempt - 1)))
                else:
                    raise last_exc

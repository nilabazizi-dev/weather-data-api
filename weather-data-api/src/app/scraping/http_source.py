from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import requests


@dataclass
class HtmlDocument:
    url: str
    fetched_at: datetime
    html: str


class HttpHtmlSource:
    def __init__(self, url: str, user_agent: str, timeout_s: float = 10.0):
        self.url = url
        self.user_agent = user_agent
        self.timeout_s = timeout_s

    def fetch(self) -> HtmlDocument:
        r = requests.get(
            self.url,
            headers={"User-Agent": self.user_agent},
            timeout=self.timeout_s,
        )
        r.raise_for_status()

        return HtmlDocument(
            url=self.url,
            fetched_at=datetime.now(timezone.utc),
            html=r.text,
        )

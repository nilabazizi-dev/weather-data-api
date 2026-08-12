from __future__ import annotations

import logging
import os
from pathlib import Path

from app.scraping.source import SnapshotFileHtmlSource, HttpHtmlSource
from app.scraping.parser import parse_current_and_forecast
from app.storage.sqlite_repo import SqliteWeatherRepository
from app.observability.metrics import (
    scrape_success_total,
    scrape_failure_total,
    scrape_duration_seconds,
)

log = logging.getLogger("scrape")


def run_scrape(repo: SqliteWeatherRepository) -> bool:
    """
    Returns:
      True  -> new snapshot inserted
      False -> duplicate (dedup)
    """
    with scrape_duration_seconds.time():
        try:
            mode = os.getenv("SCRAPE_SOURCE", "snapshot").lower()  # snapshot | http

            if mode == "http":
                target_url = os.getenv("TARGET_URL", "https://www.malteseislandsweather.com")
                user_agent = os.getenv("SCRAPER_UA", "SEN306-WeatherScraper/1.0 (+student project)")
                src = HttpHtmlSource(url=target_url, user_agent=user_agent)
                doc = src.fetch()
            else:
                html_path = Path(os.getenv("SNAPSHOT_PATH", "src/app/scraping/testdata/html/current.html"))
                src = SnapshotFileHtmlSource(html_path)
                doc = src.fetch()

            snapshot = parse_current_and_forecast(doc.html, source_url=doc.url)
            inserted = repo.save_snapshot(snapshot)

            scrape_success_total.inc()
            log.info("scrape_done", extra={"inserted": inserted, "source": doc.url})
            return inserted

        except Exception as e:
            scrape_failure_total.inc()
            log.exception("scrape_failed", extra={"error": str(e)})
            raise

from __future__ import annotations

import logging
import os
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.http.api_v1 import router
from app.observability.json_logging import setup_json_logging
from app.observability.request_logging import log_requests
from app.scraping.job import run_scrape
from app.storage.sqlite_repo import SqliteWeatherRepository

DB_PATH = Path("data/weather.db")
SCRAPE_INTERVAL_MIN = int(os.getenv("SCRAPE_INTERVAL_MIN", "30"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

setup_json_logging(LOG_LEVEL)
log = logging.getLogger("main")

app = FastAPI(title="Maltese Islands Weather API", version="1.0.0")

# middleware once
app.middleware("http")(log_requests)

# repo with Path (NOT string)
repo = SqliteWeatherRepository(db_path=DB_PATH)
repo.init_db()
app.state.repo = repo

app.include_router(router, prefix="/v1")


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


scheduler = BackgroundScheduler()


@app.on_event("startup")
def _startup():
    scheduler.add_job(lambda: run_scrape(app.state.repo), "interval", minutes=SCRAPE_INTERVAL_MIN)
    scheduler.start()
    log.info("scheduler_started", extra={"interval_min": SCRAPE_INTERVAL_MIN})


@app.on_event("shutdown")
def _shutdown():
    scheduler.shutdown()
    log.info("scheduler_stopped")

from __future__ import annotations

from app.scraping.job import run_scrape

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from app.storage.sqlite_repo import SqliteWeatherRepository

router = APIRouter()


def get_repo(request: Request) -> SqliteWeatherRepository:
    # repo is created once in main.py and stored in app.state
    return request.app.state.repo


def problem(type_: str, title: str, status: int, detail: str, instance: str):
    return JSONResponse(
        status_code=status,
        content={
            "type": type_,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": instance,
        },
        media_type="application/problem+json",
    )


@router.get("/health")
def health(repo: SqliteWeatherRepository = Depends(get_repo)):
    # simple DB readiness check
    if not repo.check_db():
        return problem(
            type_="https://example.com/problems/db-not-ready",
            title="Database not ready",
            status=503,
            detail="Database connection failed.",
            instance="/v1/health",
        )
    return {"status": "ok"}

@router.post("/admin/scrape")
def admin_scrape(repo: SqliteWeatherRepository = Depends(get_repo)):
    inserted = run_scrape(repo)
    return {"inserted": inserted}


@router.get("/weather/current")
def get_current(repo: SqliteWeatherRepository = Depends(get_repo)):
    data = repo.get_latest_current()
    if data is None:
        return problem(
            type_="https://example.com/problems/not-found",
            title="No data",
            status=404,
            detail="No current weather data stored yet. Run a scrape first.",
            instance="/v1/weather/current",
        )
    return data


@router.get("/weather/forecast")
def get_forecast(
    repo: SqliteWeatherRepository = Depends(get_repo),
    days: int = Query(..., ge=1, le=6),
):
    rows = repo.get_latest_forecast(days=days)
    if not rows:
        return problem(
            type_="https://example.com/problems/not-found",
            title="No data",
            status=404,
            detail="No forecast data stored yet. Run a scrape first.",
            instance="/v1/weather/forecast",
        )
    return {"days": days, "forecast": rows}

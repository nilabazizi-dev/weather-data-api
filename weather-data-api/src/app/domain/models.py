from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, List


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class SourceMeta:
    source_name: str
    source_url: str
    fetched_at: datetime
    parser_version: str = "v1"


@dataclass(frozen=True)
class CurrentWeather:
    observed_at: datetime
    meta: SourceMeta

    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    wind_direction: Optional[str] = None
    rainfall_mm: Optional[float] = None
    condition_text: Optional[str] = None
    condition_icon_url: Optional[str] = None


@dataclass(frozen=True)
class ForecastDay:
    # required (but can be None when you pass date=None)
    date: Optional[datetime]
    meta: SourceMeta

    # everything else truly optional now
    min_temp_c: Optional[float] = None
    max_temp_c: Optional[float] = None
    condition_text: Optional[str] = None
    condition_icon_url: Optional[str] = None
    rainfall_mm: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    wind_direction: Optional[str] = None


@dataclass(frozen=True)
class WeatherSnapshot:
    current: CurrentWeather
    forecast: List[ForecastDay]

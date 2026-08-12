from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional

from bs4 import BeautifulSoup

from app.domain.models import (
    SourceMeta,
    CurrentWeather,
    ForecastDay,
    WeatherSnapshot,
)

_NUM_C = re.compile(r"(-?\d+(?:\.\d+)?)\s*°\s*C", re.IGNORECASE)
_NUM_PCT = re.compile(r"(-?\d+(?:\.\d+)?)\s*%", re.IGNORECASE)
_NUM_MM = re.compile(r"(-?\d+(?:\.\d+)?)\s*mm\b", re.IGNORECASE)
_NUM_KMH = re.compile(r"(-?\d+(?:\.\d+)?)\s*km/?h\b", re.IGNORECASE)
_DIR = re.compile(
    r"\b(N|S|E|W|NE|NW|SE|SW|NNE|ENE|ESE|SSE|SSW|WSW|WNW|NNW)\b",
    re.IGNORECASE,
)

# ---------------- helpers ----------------

def _first_float(rx: re.Pattern, text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    m = rx.search(text)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


def _value_near_label(text: str, labels: list[str], rx: re.Pattern) -> Optional[float]:
    low = text.lower()
    for lab in labels:
        idx = low.find(lab.lower())
        if idx == -1:
            continue
        window = text[idx : idx + 500]
        val = _first_float(rx, window)
        if val is not None:
            return val
    return None


def _dir_near_label(text: str, labels: list[str]) -> Optional[str]:
    low = text.lower()
    for lab in labels:
        idx = low.find(lab.lower())
        if idx == -1:
            continue
        window = text[idx : idx + 500]
        m = _DIR.search(window)
        if m:
            return m.group(1).upper()
    return None


def _guess_condition(soup: BeautifulSoup, full_text: str) -> Optional[str]:
    for sel in ["div.condition", ".condition", ".summary", "h2", "h3"]:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(" ", strip=True)
            if 2 <= len(t) <= 80:
                return t

    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        t = meta_desc["content"].strip()
        if 2 <= len(t) <= 120:
            return t

    m = _NUM_C.search(full_text)
    if not m:
        return None
    start = max(0, m.start() - 60)
    end = min(len(full_text), m.end() + 60)
    around = full_text[start:end]
    around = _NUM_C.sub("", around).strip(" -:|")
    return around[:80] if around else None


def _clean_visible_soup(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html, "html.parser")
    # IMPORTANT: remove script/style/noscript so "wind" doesn't come from JS
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup


# ---------------- main parser ----------------

def parse_current_and_forecast(html: str, source_url: str) -> WeatherSnapshot:
    soup = _clean_visible_soup(html)

    meta = SourceMeta(
        source_name="malteseislandsweather",
        source_url=source_url,
        fetched_at=datetime.now(timezone.utc),
        # if your repo hashes include parser_version, bumping helps force a fresh insert while debugging
        parser_version="v2",
    )

    text = soup.get_text(" ", strip=True)

    temperature_c = _first_float(_NUM_C, text)
    humidity_pct = _value_near_label(text, ["humidity"], _NUM_PCT)

    # -------- WIND (try near "wind" words, then fallback to first km/h anywhere) --------
    wind_speed_kmh = _value_near_label(text, ["wind", "winds", "wind speed"], _NUM_KMH)
    wind_direction = _dir_near_label(text, ["wind", "winds", "wind speed"])

    # fallback: some pages have km/h but no "wind" label close by
    if wind_speed_kmh is None:
        wind_speed_kmh = _first_float(_NUM_KMH, text)

    # -------- RAIN (try near rain/precip words, then fallback to first mm anywhere) -----
    rainfall_mm = _value_near_label(text, ["rainfall", "rain", "precip", "precipitation"], _NUM_MM)

    # fallback: some pages have mm but no label close by
    if rainfall_mm is None:
        rainfall_mm = _first_float(_NUM_MM, text)

    condition_text = _guess_condition(soup, text)

    current = CurrentWeather(
        observed_at=meta.fetched_at,
        temperature_c=temperature_c,
        humidity_pct=int(humidity_pct) if humidity_pct is not None else None,
        wind_speed_kmh=wind_speed_kmh,
        wind_direction=wind_direction,
        rainfall_mm=rainfall_mm,
        condition_text=condition_text,
        condition_icon_url=None,
        meta=meta,
    )

    forecast = _parse_forecast_days(soup, meta)
    return WeatherSnapshot(current=current, forecast=forecast)


# ---------------- forecast ----------------

def _parse_forecast_days(soup: BeautifulSoup, meta: SourceMeta) -> list[ForecastDay]:
    blocks = soup.find_all(class_=re.compile(r"forecast", re.IGNORECASE))
    days: list[ForecastDay] = []

    if blocks:
        for b in blocks[:6]:
            btxt = b.get_text(" ", strip=True)

            temps = [_safe_float(x) for x in _NUM_C.findall(btxt)]
            temps = [t for t in temps if t is not None]
            min_t = temps[0] if len(temps) >= 1 else None
            max_t = temps[1] if len(temps) >= 2 else None

            days.append(
                ForecastDay(
                    date=None,
                    min_temp_c=min_t,
                    max_temp_c=max_t,
                    condition_text=None,
                    condition_icon_url=None,
                    rainfall_mm=_first_float(_NUM_MM, btxt),
                    wind_speed_kmh=_first_float(_NUM_KMH, btxt),
                    wind_direction=_dir_near_label(btxt, ["wind"]) or None,
                    meta=meta,
                )
            )
        return days

    # fallback if no forecast blocks
    page_text = soup.get_text(" ", strip=True)
    temps = [_safe_float(x) for x in _NUM_C.findall(page_text)]
    temps = [t for t in temps if t is not None]

    for i in range(0, min(len(temps), 12), 2):
        min_t = temps[i]
        max_t = temps[i + 1] if i + 1 < len(temps) else None

        days.append(
            ForecastDay(
                date=None,
                min_temp_c=min_t,
                max_temp_c=max_t,
                condition_text=None,
                condition_icon_url=None,
                rainfall_mm=None,
                wind_speed_kmh=None,
                wind_direction=None,
                meta=meta,
            )
        )

    return days


def _safe_float(x: str) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None
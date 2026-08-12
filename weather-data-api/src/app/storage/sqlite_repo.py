from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from app.domain.models import WeatherSnapshot

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS snapshot (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fetched_at TEXT NOT NULL,
  source_name TEXT NOT NULL,
  source_url TEXT NOT NULL,
  content_hash TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS current_weather (
  snapshot_id INTEGER PRIMARY KEY,
  observed_at TEXT NOT NULL,
  temperature_c REAL,
  humidity_pct REAL,
  wind_speed_kmh REAL,
  wind_direction TEXT,
  rainfall_mm REAL,
  condition_text TEXT,
  condition_icon_url TEXT,
  FOREIGN KEY(snapshot_id) REFERENCES snapshot(id)
);

CREATE TABLE IF NOT EXISTS forecast_day (
  snapshot_id INTEGER NOT NULL,
  day_index INTEGER NOT NULL,
  forecast_date TEXT,
  min_temp_c REAL,
  max_temp_c REAL,
  humidity_pct REAL,
  wind_speed_kmh REAL,
  wind_direction TEXT,
  rainfall_mm REAL,
  condition_text TEXT,
  condition_icon_url TEXT,
  PRIMARY KEY (snapshot_id, day_index),
  FOREIGN KEY(snapshot_id) REFERENCES snapshot(id)
);
"""


def _hash_snapshot(snapshot: WeatherSnapshot) -> str:
    d = asdict(snapshot)

    d["current"].pop("observed_at", None)
    d["current"]["meta"].pop("fetched_at", None)

    for day in d.get("forecast", []):
        day.get("meta", {}).pop("fetched_at", None)

    payload = json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class SqliteWeatherRepository:
    def __init__(self, db_path: Path):
        # Force Path even if someone accidentally passes a string
        self.db_path = Path(db_path)

    def init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # IMPORTANT: define conn
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    def save_snapshot(self, snapshot: WeatherSnapshot) -> bool:
        content_hash = _hash_snapshot(snapshot)

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()

            cur.execute("SELECT 1 FROM snapshot WHERE content_hash = ?", (content_hash,))
            if cur.fetchone():
                return False

            cur.execute(
                """
                INSERT INTO snapshot (fetched_at, source_name, source_url, content_hash)
                VALUES (?, ?, ?, ?)
                """,
                (
                    snapshot.current.meta.fetched_at.isoformat(),
                    snapshot.current.meta.source_name,
                    snapshot.current.meta.source_url,
                    content_hash,
                ),
            )
            snapshot_id = cur.lastrowid

            c = snapshot.current
            cur.execute(
                """
                INSERT INTO current_weather (
                    snapshot_id, observed_at, temperature_c, humidity_pct,
                    wind_speed_kmh, wind_direction, rainfall_mm,
                    condition_text, condition_icon_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    c.observed_at.isoformat(),
                    c.temperature_c,
                    c.humidity_pct,
                    c.wind_speed_kmh,
                    c.wind_direction,
                    c.rainfall_mm,
                    c.condition_text,
                    c.condition_icon_url,
                ),
            )

            for i, d in enumerate(snapshot.forecast[:6], start=1):
                cur.execute(
                    """
                    INSERT INTO forecast_day (
                        snapshot_id, day_index, forecast_date,
                        min_temp_c, max_temp_c, humidity_pct,
                        wind_speed_kmh, wind_direction, rainfall_mm,
                        condition_text, condition_icon_url
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot_id,
                        i,
                        getattr(d, "date", None).isoformat() if getattr(d, "date", None) else None,
                        getattr(d, "min_temp_c", None),
                        getattr(d, "max_temp_c", None),
                        getattr(d, "humidity_pct", None),
                        getattr(d, "wind_speed_kmh", None),
                        getattr(d, "wind_direction", None),
                        getattr(d, "rainfall_mm", None),
                        getattr(d, "condition_text", None),
                        getattr(d, "condition_icon_url", None),
                    ),
                )

            conn.commit()
            return True

    def check_db(self) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    def get_latest_current(self) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT cw.*
                FROM current_weather cw
                JOIN snapshot s ON s.id = cw.snapshot_id
                ORDER BY s.id DESC
                LIMIT 1
                """
            ).fetchone()
            return dict(row) if row else None

    def get_latest_forecast(self, days: int) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT fd.*
                FROM forecast_day fd
                JOIN snapshot s ON s.id = fd.snapshot_id
                WHERE s.id = (SELECT id FROM snapshot ORDER BY id DESC LIMIT 1)
                  AND fd.day_index BETWEEN 1 AND ?
                ORDER BY fd.day_index ASC
                """,
                (days,),
            ).fetchall()
            return [dict(r) for r in rows]


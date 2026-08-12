 Storage Choice and Schema Strategy


Status: Accepted

Context: We must persist observations + forecast with timestamps and metadata, deduplicate identical scrapes, and run easily via Docker and locally.

Decision: Use SQLite (data/weather.db) with a normalized schema:

    snapshot table: fetched_at, source_name, source_url, content_hash (unique)

    current_weather table: 1 row per snapshot (FK snapshot_id)

    forecast_day table: 1..6 rows per snapshot (snapshot_id, day_index)

    Use content hash deduplication to avoid writing identical records repeatedly.

Alternatives Considered

    * Postgres: scalable and production-like, but adds setup/ops overhead.

    * MongoDB: flexible, but would complicate queries and schema justification.

    * In-memory: fails persistence requirements.

 Consequences

    Positive

        * Zero-dependency local dev, simple Docker volume mapping.

        * Schema supports “latest snapshot” queries efficiently.

        * Dedup prevents DB bloat and meets requirement.

Negative

        * SQLite is single-writer; acceptable for this project’s scrape cadence.
 Architecture Style and Separation of Concerns


Status: Accepted

Context: We need an end-to-end service that scrapes weather HTML (sometimes unreliable), normalizes it into a domain model, stores it, and exposes a versioned REST API. The design must be testable, swappable (snapshot vs live HTTP), and easy to explain.

Decision: Use a layered / clean architecture approach:

    Domain layer: dataclasses for WeatherSnapshot, CurrentWeather, ForecastDay, SourceMeta.

    Scraping layer: HTML sources (snapshot file or HTTP) + parser + scrape job.

    Storage layer: repository abstraction (SqliteWeatherRepository) used by both scrape job and API.

    HTTP/API layer: FastAPI routes call repository methods only (no SQL in routes).

    Observability layer: request logging middleware + Prometheus metrics endpoint.

Alternatives Considered

    * Monolithic script (scrape + store + API in one module): fast but hard to test and change.

    * Full microservices (scraper service + API service): too heavy for scope and marks.

Consequences:

    Positive

        * Easy to swap data source (fixtures vs HTTP).

        * API remains stable even if scraper changes.

        * Repository pattern keeps DB logic isolated and testable.

    Negative

        * More files/modules than a single script.

        * Requires discipline to keep layers separated.
 API Versioning, Error Format, and Validation


Status: Accepted

Context: We must provide stable v1 endpoints, clear input validation, and standardized errors.

Decision

    Use versioned endpoints under /v1:

        GET /v1/health

        GET /v1/weather/current

        GET /v1/weather/forecast?days=1..6

        POST /v1/admin/scrape (manual trigger)

    Errors returned as RFC 7807 application/problem+json:

        Validation errors (e.g., days out of range)

        Not found/no data yet

        Internal failures mapped to generic problem response

    Enforce days validation: must be 1..6

Alternatives Considered

    1-Non-versioned endpoints: breaks future extension requirement.

    2-Plain JSON error dicts: inconsistent and less professional.

Consequences

    Positive

        Contract stability for consumers.

        Errors are predictable and documented.

        OpenAPI aligns with implementation.

    Negative

        Slightly more boilerplate for Problem Details objects.
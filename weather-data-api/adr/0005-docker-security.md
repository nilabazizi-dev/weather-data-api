 Container Base Image and Build Strategy


Status: Accepted

Context: We must containerize the system with a reproducible build and secure runtime: non-root user, minimal image, healthcheck.

Decision

    Use a slim Python base image for runtime (small, common, supported).

    Multi-stage build (if used) to avoid shipping build tools in runtime.

    Run as non-root user inside container.

    Provide HEALTHCHECK calling /v1/health.

    Configuration via env vars:

       * Port

        * DB path / volume

        * scrape mode and interval

        * log level/location (if applicable)

Alternatives Considered

    1-Full Debian/Ubuntu images: larger, slower, unnecessary.

    2-Alpine: smaller but can cause Python wheel/build complications.

Consequences

    Positive

        Matches rubric: minimal + secure + reproducible.

        Easy to run locally and in CI.

    Negative

        Requires careful dependency pinning (handled via requirements file).
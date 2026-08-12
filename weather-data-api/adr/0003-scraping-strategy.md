Scraping Cadence, Ethics, and Trigger Strategy


Status: Accepted

Context: Target site must be respected. Scraping should not hammer the website and should be robust against temporary failures. Also, assessment requires a reproducible path even if the website changes.

Decision

    Default operation uses saved HTML fixtures (snapshot mode).

    Optional live scraping uses HTTP mode with:

        * Custom User-Agent

        * Timeout on requests

        * Single request per run (no parallel scraping)

        * Interval controlled by environment variable SCRAPE_INTERVAL_MIN (recommended 30–60 minutes)

    Provide both:

        * Scheduler (APScheduler background job)

        * Admin trigger endpoint to run scrape on demand

Alternatives Considered

   1- Manual-only scraping: simpler, but not preferred vs scheduled automation.

   2- Aggressive cadence (<10 min): higher risk of blocking and unethical load.

Consequences

    Positive

        Meets ethics requirement and avoids blocks.

        Works offline (fixtures) with identical architecture.

        Clear demo: “trigger scrape → data stored → API returns results.”

    Negative

        Live HTML changes can reduce field completeness (handled by optional fields and fallbacks).
HTML Parsing Strategy and Domain Normalization



Status: Accepted

Context: HTML structure may change. We must extract current + forecast fields and normalize to a stable internal model. Some values may not exist or may be presented differently.

Decision

    Use BeautifulSoup for parsing.

    Prefer structure-based extraction (CSS selectors / nearby labels) over full-page regex.

    Remove script/style/noscript content before label searches to avoid analytics text pollution.

    Keep domain fields Optional when site does not provide a value.

    Normalize units:

        * temperature in °C

        * wind in km/h

        * rainfall in mm

    Forecast supports next 1..6 days; missing per-day details remain null rather than incorrect guesses.

Alternatives Considered

    1-Hard-coded deep CSS selectors only: brittle.

    2-Regex-only parsing from full text: too error-prone.

Consequences

    Positive

        More resilient to layout changes.

        Domain model stays stable for API consumers.

    Negative

        Some fields may still be null if the site doesn’t expose them clearly.
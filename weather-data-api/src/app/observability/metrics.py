from prometheus_client import Counter, Histogram

scrape_success_total = Counter("scrape_success_total", "Total successful scrape jobs")
scrape_failure_total = Counter("scrape_failure_total", "Total failed scrape jobs")
scrape_duration_seconds = Histogram("scrape_duration_seconds", "Scrape job duration in seconds")

Weather Data API
A Structured, Observable, and Reproducible Weather Scraping & API System

1.	Project Overview 
This project implements a complete weather data pipeline, collecting, normalizing, and storing weather data, and making it available via a versioned REST API. The system is modeled based on the principles of clean architecture, reproducible scraping, and the ability to operate observably. 
The application supports:
•	 Reliable weather data scraping using saved HTML fixtures (assessment-safe, no external dependency),
•	Optional live HTTP scraping with ethical safeguards,
•	Normalization of scraped data into a stable domain model,
•	Persistent storage in SQLite with deduplication,
•	Automated scraping via a scheduler,
•	A versioned FastAPI interface with standardized error handling,
•	Production-ready Docker packaging.
The project prioritizes maintainability, clarity of responsibility, and auditability, aligning with real-world backend engineering practices.

2.	Design Goals 
The system was constructed to meet the following objectives: 
	Reproducibility: The scraping is also achievable without the use of the internet, and saved HTML snapshots will guarantee the same results of the assessment. 
	Separation of Concerns: Scraping, parsing, persistence, API logic, and observability are tightly divided. 
	Extensibility: Storage engines, data sources, and API versions can be upgraded or switched with a minimum of effect. 
	Operational Readiness: It has health checks, metrics, structured logs, and Docker support. 

3.	High-Level Architecture
 The application has a layered architecture: 
o	Domain Layer
 Data models of concepts of weather in a pure form. 
o	Scraping Layer
In charge of getting raw HTML and extracting it into domain objects. 
o	Storage Layer 
Implements all the logic of the database as a repository abstraction. 
o	API Layer 
      Reveals versioned REST endpoints and also manages validation and error formatting
o	Observability Layer 
Presents runtime visibility metrics and structured logs. 
This design ensures that no layer is reliant on the implementation details of another.

4.	 Repository Structure
weather-data-api/
├── adr/                     # Architectural Decision Records
├── docs/                    # Architecture diagrams (C4)
├── data/                    # Runtime data (SQLite database only)
│   └── weather.db
├── src/
│   └── app/
│       ├── domain/          # Domain models
│       ├── scraping/        # HTML sources, parser, jobs, scheduler
│       ├── storage/         # SQLite repository abstraction
│       ├── http/            # FastAPI routes and controllers
│       └── observability/   # Metrics and structured logging
├── dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

5.	Architectural Decision Records (ADRs). The adr/ directory tracks all key architectural decisions. Every ADR outlines the situation, choice, options, and outcomes. 
Covered decisions include: 
•	Style of architecture and stratification, 
•	Database selection and structural design, 
•	Scraping pace and moral decisions, 
•	Versioning of API and format of error (RFC 7807), 
•	Security options and base image with Docker, 
•	HTML parsing strategy, 
•	Deduplication approach.
 These ADRs demonstrate deliberate design choices rather than ad-hoc implementation.

6.	Architecture Diagrams (C4) 
The docs/ folder holds C4 diagrams that correspond to the real structure of the code: Context Diagram - system boundaries and external actors. 
Container Diagram - significant runtime elements and data flow. 
Component Diagram - internal framework of the FastAPI application. 
The diagrams are also added in the form of PNG images to be easily reviewed. 

7.	API Design
Base URL: http://127.0.0.1:8000
Versioning
All endpoints are versioned under /v1.
This allows future versions to coexist without breaking clients.
Endpoints
Health Check: GET /v1/health
•	Verifies application startup
•	Confirms database connectivity
Current Weather
GET /v1/weather/current
Returns the most recent stored current weather snapshot.
Forecast
GET /v1/weather/forecast?days=1..6
Returns forecast data for the requested number of days.
Input validation ensures:
•	days must be between 1 and 6,
•	Invalid requests are rejected with standardized errors.
Metrics
GET /metrics
Exposes Prometheus-compatible metrics related to scraping success, failures, and duration

8.	Error Handling (RFC 7807)
 Any response to errors complies with the RFC 7807 Problem Details to HTTP APIs and is sent back as: application/problem+json 
Any response to errors contains: 
1.	type 
2.	title 
3.	status 
4.	detail 
This guarantees that there is consistent, machine-readable error handling throughout the API and that this is in full compliance with OpenAPI documentation.

9.	Scraping Strategy and Ethics
Default Mode: Snapshot Scraping: 
•	Uses saved HTML fixtures stored in the repository.
•	Ensures reproducibility and zero external dependency.
•	Recommended and used for assessment.
Optional Mode Live HTTP Scraping. 
	Can be enabled via environment configuration.
	Designed with ethical safeguards:
•	Controlled request frequency,
•	No aggressive polling,
•	Deduplication prevents redundant storage.
Deduplication 
A content hash is calculated with every scrape. In case the content is already saved, the snapshot is not saved to prevent duplication.

10.	Data Storage 
SQLite is employed in persistence because it is simple and does not require too many services to be used. 
Information is standardized in more than one table: 
•	snapshot metadata, 
•	current weather, 
•	forecast days. 
A repository layer is used to encapsulate all database access. It does not use SQL in the API layer. 

11.	Application (Docker -Recommended)
Requirements: Docker Desktop (Windows/macOS/Linux) 
Start the system
docker compose up --build
Access
•	API docs: http://127.0.0.1:8000/docs
•	Health: http://127.0.0.1:8000/v1/health
•	Metrics: http://127.0.0.1:8000/metrics
Stop
docker compose down
SQLite data is persisted using a Docker volume mapped to ./data.

12.	Running Locally (Without Docker)
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir src

13.	Environment Configuration 
A .env.example file is given to record environment variables that are needed. 
The common configuration comprises the following elements: 
	Database path, 
	Scrape mode (snapshot or HTTP), 
	Scheduler interval, 
	Optional snapshot file path. 
There are no secrets entrenched in the repository. 

14.	Observability 
The system includes: 
o	Structured JSON logging for API requests and background jobs,
o	Prometheus metrics for scrape success, failure, and execution time,
o	A health endpoint suitable for container orchestration.
These features make the system production-aware rather than a simple script.

15.	Known Data Limitations 
When there is no upstream HTML source that offers some of these forecast attributes, then those forecast attributes can be null. The system intentionally does not infer or fabricate data and preserves accuracy over completeness.

16.	Team Contributions 
This project was developed as a collaborative group effort by a team of three members. The workload was divided equally across architecture design, backend implementation, data scraping, persistence, API development, DevOps, and documentation. All members contributed to design discussions, testing, and final integration. Each member was responsible for a distinct part of the system while maintaining continuous collaboration and joint validation of the full solution.
Team Member Responsibilities:

Member 1 (Aria Insaf): Architecture, Domain & Storage Layer
Responsible for the core system design and data persistence layer.
Contributions:
•	Designed the overall architecture and clean separation of concerns
•	Defined the domain model (WeatherSnapshot, CurrentWeather, ForecastDay, SourceMeta)
•	Designed the SQLite schema and normalization strategy
•	Implemented the repository abstraction and deduplication logic
•	Implemented snapshot metadata and hashing strategy
•	Participated in ADR writing and architectural validation

Member 2 (Nilab Azizi): Scraping, Parsing & Automation
Responsible for data acquisition and normalization.
Contributions:
•	Implemented HTML snapshot source and optional HTTP source
•	Developed the HTML parsing logic and data normalization
•	Implemented snapshot-based scraping for reproducibility
•	Implemented the scraping job and APScheduler automation
•	Implemented ethical scraping controls and cadence configuration
•	Integrated scraping pipeline with persistence layer
•	Participated in ADR writing and parser design decisions

Member 3 (Arezo Behbood): API, Observability & DevOps
Responsible for the API interface, deployment, and system observability.
Contributions:
•	Implemented FastAPI REST API with versioned endpoints
•	Implemented RFC 7807 error handling (application/problem+json)
•	Implemented input validation and OpenAPI documentation
•	Implemented structured JSON logging middleware
•	Implemented Prometheus metrics and /metrics endpoint
•	Designed and implemented Dockerfile and docker-compose
•	Implemented health checks and container configuration
•	Participated in ADR writing and deployment strategy

Joint Responsibilities
All team members jointly contributed to:
•	Architectural design and decision-making
•	ADR documentation and review
•	C4 architecture diagrams
•	Integration testing and validation
•	Debugging and verification
•	README documentation and demo preparation
The project was reviewed collectively to ensure architectural consistency, correctness, and full alignment with the assessment requirements.



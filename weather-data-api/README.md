# 🌦️ Weather Data API

A structured, observable, and reproducible weather scraping and REST API system developed as a collaborative Software Engineering project.

## 📌 Overview
The system collects, normalizes, and stores weather data and provides it through a versioned FastAPI REST API.

### Key Features
- 🌐 Reproducible HTML snapshot scraping
- 🔄 Optional live HTTP scraping with ethical safeguards
- 🗄️ SQLite persistence with deduplication
- ⏰ Automated scraping with APScheduler
- 🔌 Versioned FastAPI REST API
- 📊 Prometheus metrics and structured logging
- 🐳 Docker and Docker Compose support
- 📐 C4 architecture documentation

Architecture decisions and C4 diagrams are available in the adr/ and docs/ directories

**🔌 API Endpoints**
GET /v1/health
GET /v1/weather/current
GET /v1/weather/forecast?days=1..6
GET /metrics

Interactive API documentation is available through FastAPI at:
http://127.0.0.1:8000/docs

**🛠️ Technologies**
Python FastAPI SQLite APScheduler Docker Prometheus HTML Parsing Git

**👩‍💻 My Contribution — Nilab Azizi**

**Scraping, Parsing & Automation**
Implemented HTML snapshot and optional HTTP sources
Developed HTML parsing and data normalization
Implemented reproducible snapshot-based scraping
Implemented APScheduler scraping automation
Added ethical scraping controls and cadence configuration
Integrated the scraping pipeline with the persistence layer
Participated in ADR and parser design decisions

**👥 Team**
Aria Insaf — Architecture, Domain & Storage
Nilab Azizi — Scraping, Parsing & Automation
Arezo Behbood — API, Observability & DevOps

All team members contributed to architecture, testing, documentation, integration, and final validation.

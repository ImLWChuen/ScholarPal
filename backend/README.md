# ScholarPal Backend

FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, pytest, and ruff service for ScholarPal.

## Package Architecture

```
app/
├── api/                  # API routers, v1 endpoints, and dependencies
├── core/                 # Config, database engine, and security/ownership
├── domain/               # Business modules (models & schemas)
│   ├── profile_preparation/
│   ├── scholarship_discovery/
│   ├── extraction_review/
│   ├── eligibility_impact/
│   ├── applications_interviews/
│   └── comparison/
├── repositories/         # Database persistence abstractions
├── services/             # Application services
├── clients/              # External clients (LLM structured extraction, Jev Choice)
└── jobs/                 # Scheduled background jobs and change orchestration
```

## Running Locally

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # or: source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run migrations:
   ```bash
   alembic upgrade head
   ```
4. Start the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
5. Run tests and linting:
   ```bash
   pytest
   ruff check .
   ```

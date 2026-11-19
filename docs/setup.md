# ScholarPal Setup Guide

This guide covers setting up the ScholarPal monorepo for local development and containerized deployment.

---

## Prerequisites

- **Docker & Docker Compose**: Recommended for one-command startup.
- **Python**: 3.12+ (for local development without Docker)
- **Node.js**: 22+ (for local development without Docker)
- **PostgreSQL**: 15+ (if running natively)

---

## 1. Quickstart with Docker (Recommended)

Start the entire ScholarPal stack (PostgreSQL, Backend API, Scheduler daemon, Frontend Nginx):

```bash
docker-compose up --build
```
Or with Makefile:
```bash
make docker-up
```

### Services Started:
- **Frontend**: [http://localhost:5173](http://localhost:5173) (Proxies `/api/` and `/health` to backend)
- **Backend API**: [http://localhost:8000](http://localhost:8000) (Interactive Swagger docs at `/docs`)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Database**: PostgreSQL 16 on port `5432`
- **Scheduler**: Daemon executing freshness audits & crawler synchronization

To inspect logs:
```bash
make docker-logs
```

To stop:
```bash
make docker-down
```

---

## 2. Environment Configuration

Copy the sample environment file to `.env`:

```bash
cp .env.example .env
```

Key environment options handled by `pydantic-settings`:
- `POSTGRES_SERVER`: Database host (`db` for Docker, `localhost` for local run)
- `POSTGRES_USER`: Database user (`postgres`)
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name (`scholarpal`)
- `DATABASE_URL`: Full connection string (assembled automatically if omitted)
- `RUN_MIGRATIONS`: Set to `true` to auto-apply migrations on startup
- `SEED_DATA`: Set to `true` to seed baseline scholarships and rules on startup
- `SCHEDULER_INTERVAL_SECONDS`: Periodic interval for scheduler loop

---

## 3. Seed Data Entry Point

To seed or re-seed scholarships and deterministic rules manually:

```bash
# In Docker:
docker-compose exec backend python -m app.core.seed

# Locally:
cd backend
python -m app.core.seed
```

Or via Makefile:
```bash
make seed
```

---

## 4. Local Manual Development (Without Docker)

### Backend (`/backend`)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS/Linux

pip install -e ".[dev]" greenlet
alembic upgrade head
python -m app.core.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend (`/frontend`)
```bash
cd frontend
npm install
npm run dev
```

### Crawler (`/crawler`)
```bash
cd crawler
pip install -e .
scrapy list
```

---

## 5. Verification & Testing

Run all lint and test suites:
```bash
make test
make lint
```

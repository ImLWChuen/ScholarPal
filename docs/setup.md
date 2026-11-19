# ScholarPal Setup Guide

This guide covers setting up the ScholarPal monorepo for local development.

---

## Prerequisites

- **Python**: 3.12+
- **Node.js**: 20+ (Node 22 LTS or Node 25 recommended)
- **PostgreSQL**: 15+ (running locally or via Docker)
- **Make**: (optional but recommended for unified commands)

---

## 1. Quickstart with Makefile

Run common development tasks from the repository root:

```bash
# Start dev servers (FastAPI backend on port 8000, Vite frontend on port 5173)
make dev

# Run all test suites (backend pytest and frontend check)
make test

# Run database migrations
make migrate

# Run code formatters and linters (ruff and typescript)
make lint
```

---

## 2. Environment Configuration

Copy the sample environment file to `.env`:

```bash
cp .env.example .env
```

Ensure `DATABASE_URL` matches your local PostgreSQL configuration.

---

## 3. Manual Component Setup

### Backend (`/backend`)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # On Windows
# source .venv/bin/activate # On macOS/Linux

pip install -e ".[dev]"
alembic upgrade head
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

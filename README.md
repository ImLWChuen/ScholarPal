# ScholarPal

ScholarPal is an intelligent scholarship discovery, deterministic eligibility evaluation, and application tracking platform designed for Malaysian secondary, pre-university, undergraduate, and postgraduate students.

---

## 🏛️ Monorepo Structure

```
ScholarPal/
├── .github/workflows/ci.yml   # GitHub Actions CI (Ruff lint, format, pytest, tsc, compose validate)
├── docker-compose.yml        # Multi-container stack (db, backend, scheduler, frontend)
├── backend/                  # FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2
│   ├── alembic/              # Database migration scripts & environments
│   ├── app/
│   │   ├── api/              # API routers, v1 endpoints, and dependencies
│   │   ├── core/             # Config (pydantic-settings), async DB engine, security & seed
│   │   │   ├── config.py     # Environment-driven settings (DATABASE_URL assembly, flags)
│   │   │   ├── seed.py       # Seed data entrypoint (rules, scholarships, profiles)
│   │   │   └── security.py   # Student ownership enforcement (Rule 8)
│   │   ├── domain/           # Six decoupled business modules:
│   │   │   ├── profile_preparation/
│   │   │   ├── scholarship_discovery/
│   │   │   ├── extraction_review/
│   │   │   ├── eligibility_impact/
│   │   │   ├── applications_interviews/
│   │   │   └── comparison/
│   │   ├── repositories/     # Generic async database repository patterns
│   │   ├── services/         # Application service layer
│   │   ├── clients/          # External AI clients (LLM extraction & Jev evidence check)
│   │   └── jobs/             # Scheduled background jobs & runner daemon
│   │       ├── runner.py     # Scheduler container loop with healthcheck heartbeat
│   │       └── scheduler.py  # Freshness audits & crawler synchronization
│   ├── Dockerfile            # Multi-layer backend container with healthcheck
│   ├── entrypoint.sh         # Migration runner, seed entrypoint, and Uvicorn startup
│   ├── tests/                # Pytest async test suite
│   ├── alembic.ini           # Alembic configuration
│   └── pyproject.toml        # Backend dependencies, ruff, and pytest configurations
│
├── frontend/                 # React 19 + TypeScript + Vite + React Router + TanStack Query
│   ├── src/
│   │   ├── api/              # API client and health queries
│   │   ├── components/       # UI component library (Button, Card, Badge, Input, Navbar)
│   │   ├── pages/            # View pages (Home, Scholarships, Admin Console, NotFound)
│   │   ├── routes/           # React Router route tree
│   │   ├── App.tsx           # QueryClientProvider & RouterProvider root
│   │   └── main.tsx          # Application mount point
│   ├── Dockerfile            # Multi-stage production build (Node 22 -> Nginx Alpine)
│   ├── nginx.conf            # Nginx proxy config (/api/ & /health reverse proxy)
│   └── package.json          # Frontend dependencies and build scripts
│
├── crawler/                  # Scrapy web crawler project
│   ├── crawler/
│   │   ├── items.py          # Scholarship crawled items
│   │   ├── pipelines.py      # Trafilatura + BeautifulSoup text cleaning pipelines
│   │   ├── settings.py       # Polite crawling policies and bot identification
│   │   └── spiders/          # Portal spiders
│   ├── scrapy.cfg            # Scrapy project configuration
│   └── pyproject.toml        # Scrapy dependencies
│
├── docs/                     # Architectural and domain documentation
│   ├── architecture.md       # Four-tier system architecture and data flows
│   ├── non_negotiable_rules.md # The 8 core invariant rules
│   ├── modules.md            # Detailed breakdown of the 6 domain modules
│   ├── setup.md              # Local developer environment setup guide
│   └── source_feasibility_checklist.md # Malaysian scholarship source feasibility checklist (KPH)
│
├── scripts/                  # Automation & diagnostic utility scripts
│   └── scholarship_feasibility.py # KPH source feasibility probe (robots, render, feeds, data location)
│
├── .env.example              # Sample environment configuration
├── Makefile                  # Automated commands: docker-up, test, migrate, lint, seed
├── .pre-commit-config.yaml   # Pre-commit hooks for formatting and linting
└── .gitignore                # Workspace git ignore specifications
```

---

## 🔒 Non-Negotiable Core Rules

1. **Deterministic Eligibility**: Eligibility results come only from predefined rules, never from an LLM.
2. **Three-State Requirement Evaluation**: Each requirement is `satisfied`, `unmet`, or `unresolved`. The overall verdict is:
   - *Does not meet recorded requirements* (any mandatory requirement is unmet)
   - *Needs clarification* (no mandatory requirement is unmet, but information is missing or unclear)
   - *Meets recorded requirements* (all mandatory requirements are satisfied)
3. **Assisted Admin Verification**: Jev by TypeSafe AI (`Choice` primitive) results assist the administrator and never auto-publish.
4. **Resilient Record Preservation**: Failed portal retrieval keeps the last-known record and flags uncertain freshness; it never marks a scholarship closed.
5. **Data Integrity for Missing Values**: Unknown values stay unknown (`None`/`null`), never zero.
6. **Ephemeral What-If Checks**: What-if simulations never modify saved student data.
7. **Official Portal Submissions**: Students submit on official provider portals; ScholarPal never marks submission automatically.
8. **Strict Record Ownership**: Backend enforces student ownership on every student endpoint (`403 Forbidden` on unauthorized access).

---

## ⚡ One-Command Docker Stack

The complete ScholarPal platform (PostgreSQL database, FastAPI backend, background scheduler daemon, and React Nginx frontend) runs with one command:

```bash
docker compose up --build
```
or via Makefile:
```bash
make docker-up
```

### Stack Components & Endpoints

| Container | Image / Base | Internal Port | Exposed Port | Health Check |
|---|---|---|---|---|
| `scholarpal-db` | `postgres:16-alpine` | `5432` | `5432` | `pg_isready -U postgres -d scholarpal` |
| `scholarpal-backend` | `python:3.12-slim` | `8000` | `8000` | `curl -f http://localhost:8000/health` |
| `scholarpal-scheduler`| `python:3.12-slim` | N/A | N/A | Heartbeat timestamp freshness (`/tmp/scheduler_heartbeat`) |
| `scholarpal-frontend` | `nginx:alpine` | `80` | `5173` | `wget --spider http://localhost/` |

- **Frontend Web UI**: [http://localhost:5173](http://localhost:5173)
- **Backend API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

### Automatic Migration & Seeding
On container startup, `entrypoint.sh`:
1. Waits for `scholarpal-db` health check to pass.
2. Runs database migrations automatically when `RUN_MIGRATIONS=true`.
3. Seeds initial Malaysian scholarship data and deterministic eligibility rules when `SEED_DATA=true` via `python -m app.core.seed`.

---

## 🚀 Common Makefile Commands

| Command | Description |
|---|---|
| `make docker-up` | Start all 4 containers with build in detached mode |
| `make docker-down` | Stop all Docker Compose containers |
| `make docker-logs` | Stream logs from all running containers |
| `make seed` | Manually run seed data entrypoint (`python -m app.core.seed`) |
| `make dev` | Print instructions to run `dev-backend` and `dev-frontend` in separate terminals |
| `make test` | Run pytest suite and frontend production build |
| `make lint` | Run ruff check, ruff format check, and TypeScript `tsc --noEmit` |
| `make migrate` | Run Alembic migrations locally |
| `make feasibility` | Probe official Malaysian scholarship portals and output KPH scored table |

---

## 🔄 CI / GitHub Actions

Every Pull Request automatically triggers [`.github/workflows/ci.yml`](.github/workflows/ci.yml):
- **Backend**: Python 3.12 environment, runs `ruff check .`, `ruff format --check .`, and `pytest`.
- **Frontend**: Node.js 22 environment, runs `tsc --noEmit` type checking and `npm run build`.
- **Docker Compose**: Validates `docker compose config` syntax and dependency graphs.

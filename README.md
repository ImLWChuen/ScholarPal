# ScholarPal

ScholarPal is an intelligent scholarship discovery, deterministic eligibility evaluation, and application tracking platform designed for Malaysian secondary, pre-university, undergraduate, and postgraduate students.

---

## 🏛️ Monorepo Structure

```
ScholarPal/
├── backend/                  # FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2
│   ├── alembic/              # Database migration scripts & environments
│   ├── app/
│   │   ├── api/              # API routers, v1 endpoints, and dependencies
│   │   ├── core/             # Config, async database engine, security & ownership
│   │   ├── domain/           # Six decoupled business modules:
│   │   │   ├── profile_preparation/
│   │   │   ├── scholarship_discovery/
│   │   │   ├── extraction_review/
│   │   │   ├── eligibility_impact/
│   │   │   ├── applications_interviews/
│   │   │   └── comparison/
│   │   ├── repositories/     # Generic async database repository patterns
│   │   ├── services/         # Application service layer
│   │   ├── clients/          # External AI clients:
│   │   │   ├── llm/          # Structured output extraction (never eligibility)
│   │   │   └── jev/          # Jev (Choice primitive) evidence checks (never auto-publish)
│   │   └── jobs/             # Scheduled background jobs & change orchestration
│   ├── tests/                # Pytest async test suite
│   ├── alembic.ini           # Alembic configuration
│   └── pyproject.toml        # Backend dependencies and ruff configuration
│
├── frontend/                 # React 19 + TypeScript + Vite + React Router + TanStack Query
│   ├── src/
│   │   ├── api/              # API client and health queries
│   │   ├── components/       # UI component library (Button, Card, Badge, Input, Navbar)
│   │   ├── pages/            # View pages (Home, Scholarships, Admin Console, NotFound)
│   │   ├── routes/           # React Router route tree
│   │   ├── App.tsx           # QueryClientProvider & RouterProvider root
│   │   └── main.tsx          # Application mount point
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
│   └── setup.md              # Local developer environment setup guide
│
├── .env.example              # Sample environment configuration
├── Makefile                  # Automated commands: dev, test, migrate, lint
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

## 🚀 Quickstart & Common Commands

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/ImLWChuen/ScholarPal.git
cd ScholarPal

# Copy sample environment configuration
cp .env.example .env
```

### 2. Makefile Commands
| Command | Description |
|---|---|
| `make dev` | Instructions to launch backend and frontend servers |
| `make dev-backend` | Run FastAPI backend (`uvicorn app.main:app --reload --port 8000`) |
| `make dev-frontend` | Run React Vite frontend (`npm run dev`) |
| `make migrate` | Run database migrations via Alembic |
| `make test` | Run all test suites (pytest + frontend build verification) |
| `make lint` | Run ruff lint/format checks on backend and tsc on frontend |

---

## 📖 Detailed Documentation

- [System Architecture](docs/architecture.md)
- [Non-Negotiable Rules Invariants](docs/non_negotiable_rules.md)
- [Six Domain Modules Breakdown](docs/modules.md)
- [Local Setup & Development Guide](docs/setup.md)

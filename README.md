# ScholarPal

ScholarPal is a planned scholarship discovery and application preparation platform for Malaysian students. This repository is the initial scaffold for the React and TypeScript frontend, FastAPI backend, Scrapy crawler and PostgreSQL data layer.

## Run locally

Use Python 3.12 or later and Node.js 22.12+ on the 22.x line or Node.js 24+.

From the repository root, start the API in PowerShell.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m uvicorn scholarpal.main:app --reload
```

In a second terminal at the repository root, start the frontend.

```powershell
cd frontend
npm ci
npm run dev
```

Open [the frontend](http://localhost:5173) to check whether the API responds. The health route is available at [localhost:8000/api/health](http://localhost:8000/api/health). Vite proxies `/api` requests to FastAPI during local development. This startup check requires no database or external service.

From `frontend/`, run `npm run build` to type-check and build the frontend. From `backend/`, install the optional dependencies with `python -m pip install -e ".[crawler,postgres,test]"` inside the virtual environment when working on the corresponding integrations.

With the crawler dependencies installed, run `.\.venv\Scripts\python.exe -m scrapy list` from `backend/` to check that Scrapy loads its project configuration. The spider list will be empty until the team adds approved source adapters.

## Project layout

```text
frontend/
  src/api/                      Browser client for the REST API
  src/features/                 Student workspace, authentication and admin console
backend/
  src/scholarpal/
    main.py                     FastAPI entry point
    application/
      api/                      REST routes and request validation
      auth/                     Authentication, roles and ownership checks
      jobs/                     Scheduled retrieval, reassessment and reminders
      workflows/                Review, publication and confirmed profile changes
    domain/                     Six functional modules
    infrastructure/
      ai/                       Structured LLM extraction and Jev adapters
      crawler/                  Scrapy source adapters and content cleaning
      postgres/                 PostgreSQL repositories and transactions
  migrations/                   Database schema changes
  tests/                        Automated tests
evaluation/                     Labelled datasets and prototype evaluation
```

| Proposal module | Backend under `domain/` | Frontend under `features/` |
| --- | --- | --- |
| Student profile and application preparation | `profile_preparation/` | `profile/`, `preparation/` |
| Scholarship crawler and aggregator | `scholarship_discovery/` | `scholarships/`, `admin/` |
| Information extraction and evidence review | `extraction_review/` | `admin/` |
| Explainable eligibility and change impact | `eligibility/` | `eligibility/`, `profile/` |
| Application tracking and interview management | `application_tracking/` | `applications/` |
| Scholarship and offer comparison | `comparison/` | `comparison/` |

## Planned workflow boundaries

- Retrieve and clean public source content, extract structured facts with excerpts, and send Jev evidence checks to an administrator for review. Only approved versions become public. Approved changes can trigger reassessment, preparation task updates and reminders.
- Run eligibility against approved requirements using deterministic rules. A what-if preview uses temporary values. A confirmed profile change goes through ownership checks and then triggers reassessment of affected records.
- Keep public-source AI processing separate from student data. The optional conversational assistant can call the eligibility workflow after the core features are ready.
- Store document readiness as checklist state. Students submit their applications through official provider portals.

The frontend and health endpoint are wired up. The feature directories reserve implementation space for the proposal. Database migrations, approved source adapters, background jobs, authentication and AI integrations are pending.

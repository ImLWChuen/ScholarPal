# ScholarPal Architecture

ScholarPal is an intelligent scholarship discovery, eligibility assessment, and application tracking platform designed specifically for Malaysian secondary, pre-university, undergraduate, and postgraduate students.

---

## 1. System Layers

ScholarPal adheres to a strict 4-tier clean architecture:

```
+-----------------------------------------------------------------------------------+
|                            1. PRESENTATION LAYER                                  |
|   - Student Workspace (Dashboard, Discovery, What-If Simulator, Application Tracker) |
|   - Administrator Console (Extraction Review, Evidence Inspector, Audit Logs)     |
|   - Optional Conversational Assistant                                             |
+-----------------------------------------------------------------------------------+
                                      │
                                      ▼
+-----------------------------------------------------------------------------------+
|                            2. APPLICATION LAYER                                   |
|   - FastAPI REST API Endpoints (/api/v1)                                          |
|   - Scheduled Jobs & Background Workers (Crawler synchronization, freshness audit)|
|   - Change Orchestration & Event Dispatch                                         |
+-----------------------------------------------------------------------------------+
                                      │
                                      ▼
+-----------------------------------------------------------------------------------+
|                           3. BUSINESS LOGIC LAYER                                 |
|   - Profile & Preparation                                                         |
|   - Scholarship Discovery                                                         |
|   - Extraction & Evidence Review                                                  |
|   - Eligibility & Change Impact (Predefined deterministic rules engine)           |
|   - Applications & Interviews                                                     |
|   - Comparison                                                                    |
+-----------------------------------------------------------------------------------+
                                      │
                                      ▼
+-----------------------------------------------------------------------------------+
|                          4. INFRASTRUCTURE LAYER                                  |
|   - PostgreSQL Repositories (SQLAlchemy 2.0 async engine, Alembic migrations)     |
|   - Source Retrieval & Cleaning (Scrapy, BeautifulSoup, trafilatura)              |
|   - AI Clients (LLM API with structured outputs, Jev Choice primitive)            |
+-----------------------------------------------------------------------------------+
```

---

## 2. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, React Router, TanStack Query, Lucide Icons |
| **Backend API** | FastAPI, Pydantic v2, Python 3.12+ |
| **Persistence** | PostgreSQL, SQLAlchemy 2.0 (Async), Alembic |
| **Data Ingestion** | Scrapy, BeautifulSoup4, Trafilatura |
| **AI & Verification** | LLM API (Structured JSON Schema output), Jev by TypeSafe AI (Choice primitive) |
| **Testing & Quality** | pytest, pytest-asyncio, httpx, ruff |

---

## 3. Data Flow

1. **Ingestion**: Scrapy crawls Malaysian scholarship portals. Content is extracted and cleaned using Trafilatura and BeautifulSoup.
2. **Extraction**: Clean text is submitted to LLM for structured JSON schema extraction.
3. **Verification**: Extracted criteria and claims are audited using Jev (Choice primitive) against raw source evidence.
4. **Admin Approval**: Extracted scholarships remain `pending_review` until an admin reviews and approves them.
5. **Eligibility Evaluation**: When students view scholarships, the deterministic eligibility rule engine evaluates student profile criteria against rules (satisfying rules 1, 2, and 5).
6. **Application Tracking**: Students track preparation, interview rounds, and note references. When applying, students submit directly on the provider's official portal.

---

## 4. Database Schema & Data Models

The full relational schema, table structures, foreign keys, and uniqueness constraints are documented with a Mermaid ER diagram in [docs/er_diagram.md](er_diagram.md).


.PHONY: help dev dev-backend dev-frontend test test-backend test-frontend migrate migrate-create lint lint-backend lint-frontend docker-up docker-down docker-logs seed

help:
	@echo "ScholarPal Monorepo Automation"
	@echo "Usage:"
	@echo "  make docker-up    Start entire stack via Docker Compose (db, backend, scheduler, frontend)"
	@echo "  make docker-down  Stop all Docker Compose services"
	@echo "  make docker-logs  Follow live logs from all containers"
	@echo "  make dev          Start local backend and frontend development servers"
	@echo "  make seed         Seed database with sample scholarships, rules, and demo records"
	@echo "  make test         Run backend tests (pytest) and frontend checks"
	@echo "  make migrate      Apply database migrations via Alembic"
	@echo "  make lint         Run linting (ruff for backend, tsc for frontend)"

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

seed:
	cd backend && python -m app.core.seed

dev:
	@echo "Starting backend and frontend dev servers..."
	@echo "Open separate terminals or run in parallel:"
	@echo "  Backend:  cd backend && uvicorn app.main:app --reload --port 8000"
	@echo "  Frontend: cd frontend && npm run dev"

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	cd backend && pytest

test-frontend:
	cd frontend && npm run build

migrate:
	cd backend && alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	cd backend && alembic revision --autogenerate -m "$$msg"

lint: lint-backend lint-frontend

lint-backend:
	cd backend && ruff check .
	cd backend && ruff format --check .

lint-frontend:
	cd frontend && npx tsc --noEmit

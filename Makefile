.PHONY: help dev dev-backend dev-frontend test test-backend test-frontend migrate migrate-create lint lint-backend lint-frontend

help:
	@echo "ScholarPal Monorepo Automation"
	@echo "Usage:"
	@echo "  make dev          Start backend and frontend development servers"
	@echo "  make test         Run backend tests (pytest) and frontend checks"
	@echo "  make migrate      Apply database migrations via Alembic"
	@echo "  make lint         Run linting (ruff for backend, tsc for frontend)"

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

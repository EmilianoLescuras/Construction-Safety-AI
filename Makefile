.PHONY: help install lint test api frontend up down migrate

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Install backend + dev deps into the active environment
	pip install -r requirements-backend.txt ruff pytest httpx

lint:  ## Run ruff over the Python sources (matches CI)
	ruff check src scripts tests

test:  ## Run the pytest suite (matches CI)
	pytest tests/ -v

api:  ## Serve the FastAPI backend locally on :8000
	uvicorn src.backend.app:app --host 0.0.0.0 --port 8000 --reload

frontend:  ## Run the Next.js dashboard in dev mode
	cd frontend && npm run dev

migrate:  ## Apply the latest Alembic migrations
	alembic upgrade head

up:  ## Bring up the full stack (postgres + api + frontend) via Docker
	docker compose up --build

down:  ## Tear down the Docker stack
	docker compose down

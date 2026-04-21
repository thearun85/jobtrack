.PHONY: help install fmt lint typecheck test check db-up db-down db-reset migrate clean

.DEFAULT_GOAL := help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and pre-commit hooks
	poetry install
	poetry run pre-commit install

fmt: ## Format code with ruff
	poetry run ruff format .
	poetry run ruff check --fix .

lint: ## Lint (no fixes)
	poetry run ruff check .

typecheck: ## Run mypy
	poetry run mypy

test: ## Run tests with coverage
	poetry run pytest -v -s

check: fmt lint typecheck test ## Run all checks (what CI runs)

db-up: ## Start Postgres
	docker compose up -d postgres

db-down: ## Stop Postgres
	docker compose down 

db-reset: ## Drop and recreate the database
	docker compose down -v
	docker compose up -d postgres
	@echo "Waiting for Postgres..."
	@sleep 3
	$(MAKE) migrate

migrate: ## Apply schema migrations
	poetry run python -m jobtrack.storage.migrate

clean: ## Remove caches and build artefacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info 

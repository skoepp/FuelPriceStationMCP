.DEFAULT_GOAL := help

.PHONY: install dev test lint format type-check run dev-run check clean help

install: ## Install production dependencies
	uv sync --no-dev

dev: ## Install all dependencies including dev + pre-commit hooks
	uv sync
	uv run pre-commit install

test: ## Run tests with coverage
	uv run pytest

lint: ## Run ruff linter
	uv run ruff check src tests

format: ## Run ruff formatter
	uv run ruff format src tests

format-check: ## Check formatting without modifying files
	uv run ruff format --check src tests

type-check: ## Run mypy type checker
	uv run mypy src

run: ## Run the MCP server
	uv run fuel-price-mcp

dev-run: ## Run MCP Inspector with hot-reload
	uv run mcp dev src/fuel_price_mcp/server.py

check: lint format-check type-check test ## Run all checks (lint + format + type-check + tests)

clean: ## Remove build artifacts and caches
	rm -rf dist build .eggs *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

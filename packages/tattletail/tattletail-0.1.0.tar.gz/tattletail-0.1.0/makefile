.PHONY: help install dev format lint type-check test test-cov clean build check dev-setup all

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package
	uv sync

dev: ## Install development dependencies
	uv sync --dev

format: ## Format code with ruff
	uv run ruff format ./src ./examples ./tests

lint: ## Lint code with ruff
	uv run ruff check ./src ./examples ./tests  --fix

type-check: ## Type check with pyright
	uv run pyright ./src

test: ## Run tests with pytest
	uv run pytest -v

test-integration: ## Run integration tests (requires RUN_INTEGRATION=1 and test containers up)
	@echo "Running integration tests..."
	RUN_INTEGRATION=1 uv run pytest -v tests/integration

unit-test: ## Run unit tests only
	uv run pytest tests/unit -q

bump-version: ## Bump project version (usage: make bump-version PART=patch|minor|release)
	@if [ -z "$(PART)" ]; then echo "Specify PART=patch or PART=minor or PART=release"; exit 1; fi
	uv run bump2version $(PART)

test-cov: ## Run tests with coverage
	uv run pytest --cov --cov-branch --cov-report=xml

clean: ## Clean build artifacts and cache
	rm -rf build/ || true
	rm -rf dist/ || true
	rm -rf *.egg-info/ || true
	rm -rf .pytest_cache/ || true
	rm -rf .mypy_cache/ || true
	rm -rf htmlcov/ || true
	find . -type d -name __pycache__ -delete || true
	find . -type f -name "*.pyc" -delete || true

build: ## Build the package
	uv build

check: format lint type-check test ## Run all checks

# Development workflow
dev-setup: dev ## Complete development setup
	@echo "Development environment ready!"
	@echo "Try: make demo"

all: clean format lint type-check test build ## Run complete CI/CD pipeline
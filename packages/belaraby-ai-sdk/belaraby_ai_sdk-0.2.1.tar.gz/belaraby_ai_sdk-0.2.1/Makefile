# BelArabyAI SDK Makefile

.PHONY: help install install-dev test test-cov lint format type-check build clean publish test-publish

help: ## Show this help message
	@echo "BelArabyAI SDK Development Commands"
	@echo "===================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=ba --cov-report=html --cov-report=term

lint: ## Run linting
	ruff check .
	mypy ba/

format: ## Format code
	black .
	isort .

type-check: ## Run type checking
	mypy ba/

build: ## Build the package
	python -m build

clean: ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/

publish: ## Publish to PyPI
	python scripts/publish.py

test-publish: ## Publish to TestPyPI
	python -m twine upload --repository testpypi dist/*

check: format lint type-check test ## Run all checks

all: clean install-dev check build ## Run complete development workflow

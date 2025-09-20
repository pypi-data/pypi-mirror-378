.PHONY: help install test lint format clean build update-deps

help: ## Show help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test: ## Run tests
	@make update-deps
	uv run pytest

test-cov: ## Run tests with coverage
	@make update-deps
	uv run pytest --cov=demo_example_package --cov-report=term-missing --cov-report=xml --cov-config=pyproject.toml


lint: ## Check code with linters
	@make update-deps
	uv run ruff check . --preview
	uv run ruff format .
	uv run mypy .

security: ## Run security checks
	@make update-deps
	@uv run bandit -r demo_example_package -f json -o bandit-report.json 

format: ## Format code
	@make update-deps
	uv run ruff format .
	uv run ruff check . --preview --fix

clean: ## Clean temporary files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "bandit-report.json" -delete
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

build: ## Build package
	@make update-deps
	uv build

check: ## Full pre-commit check
	@make update-deps
	@make lint
	@make test
	@make security

run-example: ## Run example
	@make update-deps
	uv run python examples/basic_usage.py.py
update-deps: ## Update dependencies and regenerate uv.lock
	uv lock

dev-setup: ## Setup development environment
	@make update-deps
	@uv sync --dev

version: ## Show current version
	@make update-deps
	@uv run python -c "import demo_example_package; print(demo_example_package.__version__)"

tags: ## List all git tags
	@git tag --sort=-version:refname

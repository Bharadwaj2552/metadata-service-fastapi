.PHONY: help install setup-dev format lint test run docs clean docker-build docker-up docker-down

help:
	@echo "Metadata Service - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install        - Install dependencies with Poetry"
	@echo "  make setup-dev      - Setup development environment"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format         - Format code with Black"
	@echo "  make lint           - Run flake8 linter"
	@echo "  make type-check     - Run mypy type checking"
	@echo "  make quality        - Run all quality checks (format, lint, type-check)"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run tests with pytest"
	@echo "  make test-cov       - Run tests with coverage report"
	@echo ""
	@echo "Development:"
	@echo "  make run            - Run application locally"
	@echo "  make migrate        - Run database migrations"
	@echo "  make docs           - Open API documentation"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-up      - Start services with docker-compose"
	@echo "  make docker-down    - Stop services"
	@echo "  make docker-logs    - View docker logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Clean up generated files"
	@echo "  make pre-commit     - Setup pre-commit hooks"

install:
	poetry install

setup-dev: install pre-commit
	@echo "✓ Development environment setup complete"

format:
	black app/ tests/
	isort app/ tests/ --profile black

lint:
	flake8 app/ tests/ --max-line-length=100 --extend-ignore=E203

type-check:
	mypy app/

quality: format lint type-check
	@echo "✓ Code quality checks passed"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

pre-commit:
	pre-commit install
	@echo "✓ Pre-commit hooks installed"

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

docs:
	@echo "Opening API documentation at http://localhost:8000/docs"
	@sleep 1
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "✓ Cleanup complete"

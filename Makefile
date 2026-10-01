# ATRA Development Makefile

.PHONY: help install dev run test lint format typecheck clean docker-build docker-up docker-down

# Help target
help:
	@echo "ATRA Development Commands:"
	@echo "  install     - Install development dependencies"
	@echo "  dev         - Run development server"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  typecheck   - Run type checking"
	@echo "  clean       - Clean generated files"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-up   - Start Docker containers"
	@echo "  docker-down - Stop Docker containers"

# Installation
install:
	pip install -e ".[dev]"

# Development server
dev:
	uvicorn atra_backend.main:app --reload --host 0.0.0.0 --port 8000

# Testing
test:
	pytest tests/ -v

lint:
	ruff check src/

format:
	ruff check --fix src/

typecheck:
	mypy src/

# Clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Database migrations
mig-revision:
	alembic revision --autogenerate -m "$(msg)"

mig-upgrade:
	alembic upgrade head

mig-downgrade:
	alembic downgrade -1
# NobleLogic Trading System Makefile

.PHONY: help install dev-install test lint format clean build run docker-build docker-run docker-dev

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  dev-install  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  clean        - Clean up temporary files"
	@echo "  build        - Build the application"
	@echo "  run          - Run the application locally"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-dev   - Run development environment with Docker"

# Installation
install:
	pip install -r requirements.txt

dev-install: install
	pip install -r requirements-dev.txt

# Testing and Quality
test:
	pytest tests/ -v --cov=backend --cov-report=html

lint:
	flake8 backend/ --max-line-length=100
	mypy backend/ --ignore-missing-imports

format:
	black backend/ --line-length=100
	isort backend/

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/
	rm -rf logs/*.log
	rm -rf data/temp/

# Build
build:
	@echo "Building NobleLogic Trading System..."
	python -m py_compile backend/*.py
	@echo "Build complete!"

# Local Development
run:
	python backend/server.py

# Docker
docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-dev:
	docker-compose -f docker-compose.dev.yml up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Configuration
config-init:
	python -c "from config import config; config.save_to_env_file('.env')"

config-validate:
	python -c "from config import get_config; cfg = get_config(); print('Configuration validated successfully')"

# Database
db-init:
	@echo "Initializing database..."
	python backend/init_data.py

# GPU Testing
gpu-test:
	python gpu_benchmark_suite.py

# Deployment
deploy-prep:
	@echo "Preparing for deployment..."
	python -m py_compile backend/*.py
	@echo "Deployment preparation complete!"

# CI/CD
ci-test: dev-install lint test
ci-build: ci-test build docker-build
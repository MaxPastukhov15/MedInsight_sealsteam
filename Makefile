.PHONY: install install-dev lint format test test-cov run clean help

# Variables
PYTHON := python3.11
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
ISORT := $(PYTHON) -m isort
MYPY := $(PYTHON) -m mypy
FLAKE8 := $(PYTHON) -m flake8

help:
	@echo "Available commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make lint         - Run all linters (mypy, flake8, black check, isort check)"
	@echo "  make format       - Format code with black and isort"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make run          - Run development server"
	@echo "  make clean        - Clean cache and build artifacts"

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements.txt

install-dev: install
	$(PIP) install pytest pytest-asyncio pytest-cov mypy black isort flake8 pre-commit
	pre-commit install

lint:
	@echo "Running mypy..."
	$(MYPY) backend/ --config-file pyproject.toml
	@echo "Running flake8..."
	$(FLAKE8) backend/
	@echo "Checking black formatting..."
	$(BLACK) --check backend/
	@echo "Checking isort..."
	$(ISORT) --check-only backend/

format:
	@echo "Formatting with black..."
	$(BLACK) backend/
	@echo "Sorting imports with isort..."
	$(ISORT) backend/

test:
	$(PYTEST) backend/tests/ -v

test-cov:
	$(PYTEST) backend/tests/ --cov=backend --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

run:
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

clean:
	@echo "Cleaning cache and build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "Clean complete!"

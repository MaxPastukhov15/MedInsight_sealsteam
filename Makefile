.PHONY: help setup dev freeze lint format check test clean

help:
	@echo "📋 Medical Analytics AI-Agent - Available targets:"
	@echo ""
	@echo "  make setup       - Create venv and install dependencies"
	@echo "  make dev        - Run backend development server"
	@echo "  make freeze     - Generate requirements.txt from pip"
	@echo "  make lint       - Run ruff check"
	@echo "  make format     - Format code with ruff"
	@echo "  make check      - Run mypy type checking"
	@echo "  make test       - Run pytest tests"
	@echo "  make clean      - Remove .venv directory"

# Try to find python3.11, fallback to python3
PYTHON := $(shell command -v python3.11 2>/dev/null || command -v python3 2>/dev/null || echo python)
VENV := .venv
PYTHON_VENV := $(VENV)/bin/python

setup: $(VENV)/bin/activate backend/requirements.txt
	$(PYTHON_VENV) -m pip install --upgrade pip
	$(PYTHON_VENV) -m pip install -r backend/requirements.txt

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)

dev: $(VENV)/bin/activate
	cd backend && $(PYTHON_VENV) -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

freeze:
	$(PYTHON_VENV) -m pip freeze > backend/requirements.txt

lint:
	$(PYTHON_VENV) -m ruff check backend/

format:
	$(PYTHON_VENV) -m ruff format backend/

check:
	$(PYTHON_VENV) -m mypy backend/

test:
	@echo "⚠️  Tests are stubs (WIP). Most test files are in black-box mode."
	@echo "Run actual tests when implementation is ready:"
	@echo "  $(PYTHON_VENV) -m pytest backend/tests/ -v"
	# $(PYTHON_VENV) -m pytest backend/tests/ -v --cov=backend

clean:
	rm -rf $(VENV)

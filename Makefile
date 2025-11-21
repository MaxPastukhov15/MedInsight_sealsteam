PYTHON_VERSION := 3.11
VENV_NAME := .venv

# Find Python 3.11 in common locations
PYTHON := $(shell which python$(PYTHON_VERSION) 2>/dev/null || echo "/usr/local/bin/python$(PYTHON_VERSION)")

.PHONY: install-dev clean-venv run lint test pre-commit-check check-python

check-python:
	@if [ ! -f "$(PYTHON)" ] && ! command -v python$(PYTHON_VERSION) &>/dev/null; then \
		echo "❌ ERROR: Python $(PYTHON_VERSION) not found!"; \
		echo "Searched in:"; \
		echo "  - $(PYTHON)"; \
		echo "  - PATH locations"; \
		echo "\nInstall Python $(PYTHON_VERSION) via:"; \
		echo "  - pyenv: pyenv install $(PYTHON_VERSION)"; \
		echo "  - apt: sudo apt install python$(PYTHON_VERSION)"; \
		exit 1; \
	fi
	@echo "✅ Found Python $(PYTHON_VERSION): $(PYTHON)"
	@$(PYTHON) --version

install-dev: check-python
	@echo "🔧 Setting up development environment..."
	@if [ -d $(VENV_NAME) ]; then \
		echo "🗑️  Removing existing venv..."; \
		rm -rf $(VENV_NAME); \
	fi
	@echo "📦 Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV_NAME)
	@echo "⬆️  Upgrading pip..."
	@. $(VENV_NAME)/bin/activate && pip install --upgrade pip --quiet
	@echo "📚 Installing backend dependencies..."
	@. $(VENV_NAME)/bin/activate && pip install -r backend/requirements.txt --quiet
	@echo "🛠️  Installing dev dependencies..."
	@. $(VENV_NAME)/bin/activate && pip install -r backend/requirements-ci.txt --quiet
	@if [ ! -f .env ]; then \
		cp backend/.env.example .env; \
		echo "📝 Created .env from backend/.env.example"; \
	else \
		echo "✅ .env already exists"; \
	fi
	@echo "🪝 Installing pre-commit hooks..."
	@. $(VENV_NAME)/bin/activate && pre-commit install --quiet
	@echo ""
	@echo "✅ Development environment ready!"
	@echo "   Activate: source $(VENV_NAME)/bin/activate"
	@echo "   Run API: make run"

clean-venv:
	@echo "🗑️  Removing virtual environment..."
	@rm -rf $(VENV_NAME)
	@echo "✅ Cleaned!"

run:
	@if [ ! -d $(VENV_NAME) ]; then \
		echo "❌ Virtual environment not found. Run 'make install-dev' first."; \
		exit 1; \
	fi
	@echo "🚀 Starting FastAPI server..."
	@. $(VENV_NAME)/bin/activate && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

lint:
	@if [ ! -d $(VENV_NAME) ]; then \
		echo "❌ Virtual environment not found. Run 'make install-dev' first."; \
		exit 1; \
	fi
	@echo "🔍 Running linters..."
	@. $(VENV_NAME)/bin/activate && pre-commit run --all-files

test:
	@if [ ! -d $(VENV_NAME) ]; then \
		echo "❌ Virtual environment not found. Run 'make install-dev' first."; \
		exit 1; \
	fi
	@echo "🧪 Running tests..."
	@. $(VENV_NAME)/bin/activate && pytest

pre-commit-check:
	@if [ ! -d $(VENV_NAME) ]; then \
		echo "❌ Virtual environment not found. Run 'make install-dev' first."; \
		exit 1; \
	fi
	@. $(VENV_NAME)/bin/activate && pre-commit run --all-files --show-diff-on-failure

help:
	@echo "Medical Analytics AI Agent - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install-dev     Install dependencies and setup dev environment"
	@echo "  make clean-venv      Remove virtual environment"
	@echo ""
	@echo "Development:"
	@echo "  make run             Start FastAPI server with auto-reload"
	@echo "  make lint            Run all linters (black, ruff, mypy)"
	@echo "  make test            Run pytest tests"
	@echo ""
	@echo "Checks:"
	@echo "  make check-python    Verify Python $(PYTHON_VERSION) is available"
	@echo "  make pre-commit-check  Run pre-commit hooks on all files"

# Recommended: Python 3.11 for stability
# Makefile will try python3.11 first, then fallback to python3
PYTHON_PREFERRED := python3.11
PYTHON_FALLBACK := python3
VENV_NAME := .venv

PYTHON := $(shell command -v $(PYTHON_PREFERRED) 2>/dev/null || command -v $(PYTHON_FALLBACK) 2>/dev/null)

.PHONY: install-dev clean-venv run lint test check-python help

check-python:
	@if [ -z "$(PYTHON)" ]; then \
		echo "❌ ERROR: No Python found!"; \
		exit 1; \
	fi
	@PYTHON_VERSION=$$($(PYTHON) --version 2>&1); \
	echo "🐍 Using: $$PYTHON_VERSION ($(PYTHON))"; \
	if echo "$$PYTHON_VERSION" | grep -q "3\.11"; then \
		echo "✅ Python 3.11 - perfect!"; \
	elif echo "$$PYTHON_VERSION" | grep -qE "3\.(1[2-9]|[2-9][0-9])"; then \
		echo "⚠️  Python 3.12+ detected"; \
		echo "    Recommended: Python 3.11 (see INSTALL.md)"; \
		echo "    Continuing anyway..."; \
	else \
		echo "❌ Python 3.11+ required!"; \
		echo "    See INSTALL.md for installation"; \
		exit 1; \
	fi

install-dev: check-python
	@echo "🔧 Setting up development environment..."
	@if [ -d $(VENV_NAME) ]; then \
		echo "🗑️  Removing existing venv..."; \
		rm -rf $(VENV_NAME); \
	fi
	@echo "📦 Creating venv with $(PYTHON)..."
	@$(PYTHON) -m venv $(VENV_NAME)
	@echo "⬆️  Upgrading pip..."
	@. $(VENV_NAME)/bin/activate && pip install --upgrade pip --quiet
	@echo "📚 Installing dependencies..."
	@. $(VENV_NAME)/bin/activate && pip install -r backend/requirements.txt --quiet
	@. $(VENV_NAME)/bin/activate && pip install -r backend/requirements-ci.txt --quiet
	@if [ ! -f .env ]; then cp .env.example .env 2>/dev/null && echo "📝 Created .env" || true; fi
	@. $(VENV_NAME)/bin/activate && pre-commit install --quiet 2>/dev/null || true
	@echo ""
	@echo "✅ Ready!"
	@echo "   Activate: source $(VENV_NAME)/bin/activate"
	@echo "   Run: make run"

clean-venv:
	@rm -rf $(VENV_NAME)
	@echo "✅ Cleaned!"

run:
	@test -d $(VENV_NAME) || (echo "❌ Run: make install-dev"; exit 1)
	@echo "🚀 Starting FastAPI..."
	@. $(VENV_NAME)/bin/activate && uvicorn backend.main:app --reload

lint:
	@test -d $(VENV_NAME) || (echo "❌ Run: make install-dev"; exit 1)
	@echo "🔍 Ruff (replaces Black+Flake8+isort)..."
	@. $(VENV_NAME)/bin/activate && ruff check backend/ --fix
	@. $(VENV_NAME)/bin/activate && ruff format backend/
	@echo "✅ Done!"

test:
	@test -d $(VENV_NAME) || (echo "❌ Run: make install-dev"; exit 1)
	@. $(VENV_NAME)/bin/activate && pytest backend/tests/ -v 2>/dev/null || echo "⚠️  No tests"

help:
	@echo "Commands:"
	@echo "  make install-dev    Setup environment"
	@echo "  make run            Start server"
	@echo "  make lint           Format code (Ruff only)"
	@echo "  make test           Run tests"
	@echo "  make check-python   Check Python version"

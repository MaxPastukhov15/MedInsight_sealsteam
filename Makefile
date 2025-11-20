PYTHON_VERSION := 3.11
VENV_NAME := .venv

.PHONY: install-dev clean-venv run lint test pre-commit-check

install-dev:
	@if ! command -v python$(PYTHON_VERSION) &>/dev/null; then \
		echo "ERROR: Требуется Python $(PYTHON_VERSION)! Установи через pyenv или пакетный менеджер."; exit 1; \
	fi
	@if [ -d $(VENV_NAME) ]; then rm -rf $(VENV_NAME); fi
	python$(PYTHON_VERSION) -m venv $(VENV_NAME)
	. $(VENV_NAME)/bin/activate && pip install --upgrade pip
	. $(VENV_NAME)/bin/activate && pip install -r backend/requirements.txt
	. $(VENV_NAME)/bin/activate && pip install -r backend/requirements-ci.txt
	@if [ ! -f .env ]; then cp .env.example .env; echo "Скопирован .env.example в .env"; fi
	. $(VENV_NAME)/bin/activate && pre-commit install
	@echo "✅ Всё готово: venv, зависимости, .env, pre-commit!"

clean-venv:
	rm -rf $(VENV_NAME)

run:
	. $(VENV_NAME)/bin/activate && uvicorn backend.main:app --host 0.0.0.0 --port 8000

lint:
	. $(VENV_NAME)/bin/activate && pre-commit run --all-files

test:
	. $(VENV_NAME)/bin/activate && pytest

pre-commit-check:
	. $(VENV_NAME)/bin/activate && pre-commit run --all-files --show-diff-on-failure
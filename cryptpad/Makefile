SHELL := /bin/bash

.DEFAULT_GOAL := test

POETRY_HELPER_DIR ?= /tmp/cryptpad-poetry-verify
POETRY_VENV_ROOT ?= /tmp/cryptpad-poetry-venvs
POETRY_BIN := $(POETRY_HELPER_DIR)/bin/poetry

.PHONY: up down test test-backend test-ui test-image test-compose poetry-helper

poetry-helper:
	@if [ ! -x "$(POETRY_BIN)" ]; then \
		python3 -m venv "$(POETRY_HELPER_DIR)" && \
		"$(POETRY_HELPER_DIR)/bin/pip" install --quiet poetry; \
	fi

up:
	docker compose up -d --build

down:
	docker compose down -v

test:
	@$(MAKE) --no-print-directory test-backend
	@echo "== backend ok =="
	@$(MAKE) --no-print-directory test-ui
	@echo "== ui ok =="
	@$(MAKE) --no-print-directory test-image
	@echo "== image ok =="
	@$(MAKE) --no-print-directory test-compose
	@echo "== compose ok =="
	@echo "== all tests passed =="

test-backend: poetry-helper
	@cd rmcryptpad && \
		unset VIRTUAL_ENV CONDA_PREFIX PYTHONHOME PYTHONPATH && \
		export POETRY_VIRTUALENVS_PATH="$(POETRY_VENV_ROOT)"; \
		export PATH="$(POETRY_HELPER_DIR)/bin:$$PATH"; \
		poetry install --no-interaction && \
		VENV_PATH="$$(poetry env info -p)" && \
		"$$VENV_PATH/bin/pytest" -v

test-ui:
	cd rmcryptpad/ui && pnpm install --frozen-lockfile && pnpm test -- --run

test-image:
	sh tests/test_cryptpad_image.sh

test-compose:
	bash tests/test_compose_smoke.sh

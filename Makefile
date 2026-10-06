.DEFAULT_GOAL := help
PROFILE ?= core
.PHONY: help doctor setup up down test lint fmt load-graph ask eval

help:        ## List targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-11s %s\n", $$1, $$2}'
doctor:      ## Check prerequisites
	python scripts/doctor.py
setup:       ## Install Python dependencies (uv workspace)
	uv sync --all-packages --dev
up:          ## Start a profile: make up PROFILE=core|full
	docker compose --profile $(PROFILE) up -d
down:        ## Stop everything
	docker compose --profile core --profile full down
test:        ## Unit + contract tests
	uv run pytest -q
lint:        ## Lint
	uv run ruff check .
fmt:         ## Format
	uv run ruff format .
load-graph ask eval:   ## Implemented in later milestones (PLAN.md §13)
	@echo "'$@' arrives in a later milestone — see PLAN.md §13"; exit 1

.PHONY: help setup deploy destroy verify clean install

# Load environment variables if .env exists
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Default target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@python -c "import re; lines = open('Makefile', encoding='utf-8').readlines(); targets = [(m.group(1), m.group(2)) for line in lines if (m := re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line))]; [print(f'  {name:15} {desc}') for name, desc in targets]"

install: ## Install Python dependencies
	@uv pip install -e .

bootstrap: ## Create OU structure (idempotent - safe to re-run)
	@python -m scripts.bootstrap

setup: ## Deploy pipeline role to management account (one-time setup)
	@python -m scripts.org_setup

verify: ## Verify pipeline setup
	@python -m scripts.org_setup --verify

deploy: ## Deploy all StackSets and SCPs
	@python -m scripts.deploy

status: ## Show current deployment status
	@python -m scripts.status

all: bootstrap setup deploy ## Complete deployment (OUs + Pipeline Role + StackSets)
	@echo ========================================================
	@echo   DEPLOYMENT COMPLETE
	@echo ========================================================

destroy: ## Destroy all infrastructure (requires confirmation)
	@python -m scripts.deploy --destroy

clean: ## Clean Python cache files
	@python -c "import pathlib; import shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]; [p.unlink() for p in pathlib.Path('.').rglob('*.pyc')]; [p.unlink() for p in pathlib.Path('.').rglob('*.pyo')]; print('Cache cleaned')"

# Testing targets
test: ## Run all tests
	@uv run pytest tests/ -v

test-unit: ## Run unit tests only
	@uv run pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@uv run pytest tests/integration/ -v

test-coverage: ## Run tests with coverage report
	@uv run pytest tests/ --cov=src/ai_org --cov-report=term-missing --cov-report=html

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@uv run pytest-watch tests/unit/ -v

# Quality targets
pre-commit: ## Run all quality checks (lint, format, typecheck)
	@uv run pre-commit run --all-files

lint: ## Run ruff linting only
	@uv run ruff check src/ tests/ scripts/

format: ## Format code with ruff only
	@uv run ruff format src/ tests/ scripts/

typecheck: ## Run mypy type checking only
	@uv run mypy src/

# Docker targets (legacy, kept for compatibility)
claude: ## Launch Claude Code (cross-platform version)
	@echo "Launching Claude Code (new cross-platform version)..."
	@docker-compose up -d dev
	@echo "Waiting for container to be ready..."
	@python -c "import time; time.sleep(1)"
	@docker-compose exec -it dev claude $(ARGS)

claude-x: ## Launch Claude Code cross-platform with skip permissions
	@$(MAKE) claude ARGS='--dangerously-skip-permissions -c'

claude-debug: ## Launch Claude Code with skip permissions flag
	@$(MAKE) claude ARGS='--dangerously-skip-permissions -c --debug'

join-claude: ## Open bash shell in Claude container
	@echo "Joining Claude container with bash shell..."
	@docker-compose exec -it dev /bin/bash

docker-build: ## Build Docker containers
	docker-compose build

docker-stop: ## Stop Docker containers
	docker-compose down

docker-clean: ## Clean Docker containers and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

codex: ## Launch Codex search
	@echo "Launching Codex..."
	@docker-compose up -d dev
	@echo "Waiting for container to be ready..."
	@python -c "import time; time.sleep(1)"
	@docker-compose exec -it dev codex --dangerously-bypass-approvals-and-sandbox --search $(ARGS)

docs: ## Generate API documentation with pdoc
	@echo "Generating API documentation..."
	@uv pip install -q pdoc
	@uv run pdoc --output-dir pdoc --html --force ai_org
	@mv pdoc/ai_org/* pdoc/ 2>/dev/null || true
	@rmdir pdoc/ai_org 2>/dev/null || true
	@echo "Documentation generated in ./pdoc/"

docs-serve: ## Generate and serve API documentation
	@echo "Generating and serving API documentation..."
	@uv pip install -q pdoc
	@uv run pdoc --http localhost:8080 ai_org

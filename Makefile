.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message.
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Create virtual environment and install all dependencies (Python and npm).
	@echo "Creating virtual environment using pyenv and poetry"
	@poetry install
	@poetry run pre-commit install
	@echo "Installing npm dependencies"
	@cd web && npm install

.PHONY: check
check: ## Run checks: lock file consistency, linting, and obsolete dependency check.
	@echo "Checking Poetry lock file consistency with 'pyproject.toml': Running poetry check --lock"
	@poetry check --lock
	@echo "Linting code: Running pre-commit"
	@poetry run pre-commit run -a
	@echo "Checking for obsolete dependencies: Running deptry"
	@poetry run deptry .

.PHONY: docker-build
docker-build: ## Build the bitvoker Docker image.
	docker build -t bitvoker -f Dockerfile .

.PHONY: docker-run
docker-run: ## Run the container named bitvoker using the bitvoker image.
	docker volume create bitvoker_data && docker run -p 8084:8084 -p 8085:8085 -v bitvoker_data:/app/data -v /etc/localtime:/etc/localtime:ro --name bitvoker bitvoker

.PHONY: docker
docker: clean docker-build docker-run

.PHONY: clean
clean: ## Clean Docker containers, volumes, Python cache, build artifacts and temporary files.
	@echo "Cleaning Docker resources..."
	-docker rm -f bitvoker 2>/dev/null || true
	-docker volume rm bitvoker_data 2>/dev/null || true
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -name ".pytest_cache" -exec rm -rf {} +
	find . -name ".coverage" -delete
	find . -name "htmlcov" -exec rm -rf {} +
	@echo "Cleaning build artifacts..."
	rm -rf dist/ build/
	@echo "Cleaning log files..."
	find . -name "*.log" -delete
	@echo "Clean complete"
	@echo "Cleaning React/npm files..."
	rm -rf web/node_modules || true
	rm -rf web/build || true
	rm -rf web/.cache || true
	rm -rf web/coverage || true
	find web -name ".npm" -exec rm -rf {} + 2>/dev/null || true

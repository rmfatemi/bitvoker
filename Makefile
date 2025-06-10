.DEFAULT_GOAL := docker

.PHONY: help
help: ## show this help message.
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## create virtual environment and install all dependencies (Python and npm).
	@echo "creating virtual environment using pyenv and poetry"
	@poetry install
	@poetry run pre-commit install
	@echo "installing npm dependencies"
	@cd web && npm install

.PHONY: check
check: ## run checks: lock file consistency, linting, and obsolete dependency check.
	@echo "checking Poetry lock file consistency with 'pyproject.toml': Running poetry check --lock"
	@poetry check --lock
	@echo "linting code: Running pre-commit"
	@poetry run pre-commit run -a
	@echo "checking for obsolete dependencies: Running deptry"
	@poetry run deptry .

.PHONY: docker-build
docker-build: ## build the bitvoker Docker image.
	docker build -t bitvoker -f Dockerfile .

.PHONY: docker-run
docker-run: ## run the container named bitvoker using the bitvoker image.
	docker volume create bitvoker_data && docker run -p 8083:8083 -p 8084:8084 -p 8085:8085 -p 8086:8086 -v bitvoker_data:/app/data -v /etc/localtime:/etc/localtime:ro --name bitvoker bitvoker

.PHONY: docker
docker: clean docker-build docker-run

.PHONY: clean
clean: ## clean Docker containers, volumes, Python cache, build artifacts and temporary files.
	@echo "cleaning Docker resources..."
	-docker rm -f bitvoker 2>/dev/null || true
	-docker volume rm bitvoker_data 2>/dev/null || true
	@echo "cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -name ".pytest_cache" -exec rm -rf {} +
	find . -name ".coverage" -delete
	find . -name "htmlcov" -exec rm -rf {} +
	@echo "cleaning build artifacts..."
	rm -rf dist/ build/
	@echo "cleaning log files..."
	find . -name "*.log" -delete
	@echo "clean complete"
	@echo "cleaning React/npm files..."
	rm -rf web/node_modules || true
	rm -rf web/build || true
	rm -rf web/.cache || true
	rm -rf web/coverage || true
	find web -name ".npm" -exec rm -rf {} + 2>/dev/null || true

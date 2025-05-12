.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message.
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Create virtual environment and install dependencies.
	@echo "Creating virtual environment using pyenv and poetry"
	@poetry install
	@poetry run pre-commit install

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
	docker build -t bitvoker -f docker/Dockerfile .

.PHONY: docker-run
docker-run: ## Run the container named bitvoker-container using the bitvoker image.
	mkdir -p docker-tmp-data
	docker run --rm -p 8084:8084 -p 8085:8085 -v $(PWD)/docker-tmp-data:/app/data --name bitvoker-container bitvoker

.PHONY: docker-clean
docker-clean: ## Remove the bitvoker-container and clean up the docker-tmp-data directory.
	-docker rm -f bitvoker-container 2>/dev/null || true
	rm -rf docker-tmp-data || true

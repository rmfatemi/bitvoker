.DEFAULT_GOAL := help

.PHONY: help
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install:
	@echo "Creating virtual environment using pyenv and poetry"
	@poetry install
	@poetry run pre-commit install

.PHONY: check
check:
	@echo "Checking Poetry lock file consistency with 'pyproject.toml': Running poetry check --lock"
	@poetry check --lock
	@echo "Linting code: Running pre-commit"
	@poetry run pre-commit run -a
	@echo "Checking for obsolete dependencies: Running deptry"
	@poetry run deptry .

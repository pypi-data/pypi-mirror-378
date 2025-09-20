# Trainwave Jupyter Extension Makefile
# This Makefile provides convenient targets for building, testing, and managing the project

PROJECT_NAME          := trainwave-jupyter
BASE_DIR              := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

VERSION_LONG          := $(shell git describe --first-parent --abbrev=10 --long --tags --dirty)
VERSION_SHORT         := $(shell echo $(VERSION_LONG) | cut -f 1 -d "-")
DATE_STRING           := $(shell date +'%m-%d-%Y')
GIT_HASH              := $(shell git rev-parse --verify HEAD)

# Formatting variables
BOLD                  := $(shell tput bold)
RESET                 := $(shell tput sgr0)
RED                   := $(shell tput setaf 1)
GREEN                 := $(shell tput setaf 2)
YELLOW                := $(shell tput setaf 3)
TEAL                  := $(shell tput setaf 6)

JLPM = uv run jlpm

.PHONY: install
install: build-prod ## Install the extension in production mode
	@echo "Installing trainwave-jupyter extension..."
	uv pip install -e .
	jupyter labextension install . --no-build
	@echo "Extension installed successfully!"

.PHONY: install-dev
install-dev: build ## Install the extension in development mode
	@echo "Installing trainwave-jupyter extension in development mode..."
	uv pip install -e ".[test]"
	uv run jupyter labextension develop . --overwrite
	uv run jupyter server extension enable trainwave_jupyter
	uv run jlpm build
	@echo "Extension installed in development mode!"

.PHONY: build
build: ## Build the extension in development mode
	@echo "Building extension in development mode..."
	$(JLPM) build
	@echo "Build complete!"

.PHONY: build-prod
build-prod: ## Build the extension for production
	@echo "Building extension for production..."
	$(JLPM) build:prod
	@echo "Production build complete!"

.PHONY: clean
clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	$(JLPM) clean:all
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	@echo "Clean complete!"

.PHONY: clean-all
clean-all: clean ## Clean everything including node_modules and Python cache
	@echo "Cleaning everything..."
	rm -rf node_modules/
	rm -rf .pytest_cache/
	rm -rf coverage/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Deep clean complete!"

.PHONY: verify-build
verify-build: ## Verify the build is ready for publishing
	@echo "Verifying build for publishing..."
	./scripts/verify-build.sh

.PHONY: release
release: ## Create a new release (interactive)
	@echo "Creating a new release..."
	./scripts/create-release.sh

.PHONY: test
test: ## Run all tests
	@echo "Running tests..."
	./run-tests.sh

.PHONY: lint
lint: ## Run all linting checks
	@echo "Running linting checks..."
	$(JLPM) lint:check
	uv run ruff check trainwave_jupyter/
	@echo "Linting complete!"

.PHONY: lint-fix
lint-fix: ## Fix linting issues
	@echo "Fixing linting issues..."
	$(JLPM) lint
	uv run ruff check --fix trainwave_jupyter/
	uv run black ./
	@echo "Linting fixes applied!"

.PHONY: format
format: ## Format code
	@echo "Formatting code..."
	$(JLPM) prettier
	uv run black ./
	uv run ruff format trainwave_jupyter/
	@echo "Code formatted!"

.PHONY: watch
watch: ## Watch for changes and rebuild automatically
	@echo "Starting watch mode..."
	uv run jlpm watch

.PHONY: dev
dev: install-dev watch ## Start development mode (install + watch)

.PHONY: uninstall-extension
uninstall-extension: ## Uninstall the extension
	@echo "Uninstalling trainwave-jupyter extension..."
	uv run jupyter labextension uninstall trainwave-jupyter
	uv pip uninstall trainwave-jupyter -y
	@echo "Extension uninstalled!"

.PHONY: package
package: build-prod ## Create distribution packages
	@echo "Creating distribution packages..."
	uv build
	@echo "Packages created in dist/"

.PHONY: start-server
start-server: ## Start JupyterLab server
	@echo "Starting JupyterLab server..."
	uv run jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root

.PHONY: check
check: ## Run all checks (lint, test, build)
	@echo "Running all checks..."
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) build-prod
	@echo "All checks passed!"

.PHONY: deploy
deploy: clean build-prod package ## Full production deployment
	@echo "Production deployment ready!"
	@echo "Packages available in dist/"

.PHONY: version
version: ## Print the version
	@echo $(VERSION_LONG)

.DEFAULT_GOAL := help

.PHONY: help
help:  ## Print this make target help message
	@echo "$(BOLD)Trainwave Make Targets$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make $(TEAL)<target>$(RESET)\n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n$(TEAL)%s$(RESET)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@printf "\n"


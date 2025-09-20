# Makefile for desto package management

.PHONY: help bump-patch bump-minor bump-major release-patch release-minor release-major build test lint clean

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Version bumping
bump-patch:  ## Bump patch version (0.1.14 -> 0.1.15)
	python scripts/bump_version.py patch

bump-minor:  ## Bump minor version (0.1.14 -> 0.2.0)
	python scripts/bump_version.py minor

bump-major:  ## Bump major version (0.1.14 -> 1.0.0)
	python scripts/bump_version.py major

# Release process
release-patch:  ## Bump patch version and create release
	./scripts/release.sh patch

release-minor:  ## Bump minor version and create release
	./scripts/release.sh minor

release-major:  ## Bump major version and create release
	./scripts/release.sh major

# Development
test-parallel:  ## Run tests in parallel
	uv run --extra dev pytest -n auto tests/

test:  ## Run tests
	uv run --extra dev pytest tests/

lint:  ## Run linting
	uv run --extra dev ruff check .

lint-fix:  ## Run linting and auto-fix issues
	uv run --extra dev ruff check . --fix

build:  ## Build package
	uv build

clean:  ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info/

# Quick development tasks
dev-install:  ## Install package in development mode with dev dependencies
	uv sync --extra dev

docs-build: docs-sync-readme  ## Install docs dependencies and build the MkDocs documentation site
	uv sync --extra docs
	uv run --extra docs mkdocs build -f mkdocs.yml

docs-serve:  ## Install docs dependencies and serve the MkDocs site locally at http://127.0.0.1:8000
	uv sync --extra docs
	# Use uv run so the correct project venv and deps are used
	uv run --extra docs mkdocs serve -f mkdocs.yml

publish:  ## Publish to PyPI (manual - normally done by GitHub Actions)
	@echo "⚠️  Note: Publishing is normally automated via GitHub Actions"
	@echo "🚀 To publish: git tag vX.Y.Z && git push --tags"
	@echo ""
	@echo "🔄 Manual publish (not recommended):"
	uv publish

# Show current version
version:  ## Show current version
	@python -c "import sys; sys.path.insert(0, 'src'); from desto._version import __version__; print(f'Current version: {__version__}')"

# Check release status
check-release:  ## Check if current version is published
	@python -c "import sys, requests; sys.path.insert(0, 'src'); from desto._version import __version__; r=requests.get(f'https://pypi.org/pypi/desto/{__version__}/json'); print(f'✅ Version {__version__} is published' if r.status_code==200 else f'❌ Version {__version__} not found on PyPI')"

# Docker commands
docker-stop:  ## Stop and remove Docker container
	docker stop desto-dashboard || true
	docker rm desto-dashboard || true

docker-logs:  ## View Docker container logs
	docker logs -f desto-dashboard

docker-start:  ## Start desto with Redis
	docker compose up -d

docker-stop-all:  ## Stop all desto services (including Redis)
	docker compose down

docker-redis-logs:  ## View Redis logs
	docker logs -f desto-redis

docker-test:  ## Run Docker integration tests (excluding slow/hanging tests)
	uv run --extra dev pytest tests/test_docker_integration.py -k "not test_docker_run_health_check and not test_docker_build" -v

docker-test-full:  ## Run all Docker integration tests (including slow ones)
	uv run --extra dev pytest tests/test_docker_integration.py -v

docker-setup-examples:  ## Setup Docker example scripts
	mkdir -p desto_scripts desto_logs
	chmod +x desto_scripts/*.sh 2>/dev/null || true
	@echo "✅ Docker setup complete - desto_scripts/ and desto_logs/ ready"
	@echo "📁 Example scripts available in desto_scripts/"

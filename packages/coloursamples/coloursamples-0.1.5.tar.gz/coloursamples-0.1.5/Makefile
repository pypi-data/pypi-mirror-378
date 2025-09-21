# Makefile for coloursamples project

.PHONY: help install test coverage lint format build clean release pre-release-check

# Default target
help:
	@echo "Available commands:"
	@echo "  install           Install the package and dev dependencies"
	@echo "  test              Run tests"
	@echo "  coverage          Run tests with coverage report"
	@echo "  lint              Run linting checks"
	@echo "  format            Format code"
	@echo "  build             Build the package"
	@echo "  clean             Clean build artifacts"
	@echo "  pre-release-check Run pre-release checks"
	@echo "  release           Create a new release (use VERSION=x.x.x)"

# Install package and dev dependencies
install:
	uv sync --group dev

# Run tests
test:
	uv run pytest

# Run tests with coverage
coverage:
	uv run pytest --cov=coloursamples --cov-report=html --cov-report=term

# Run linting
lint:
	uv run ruff check .

# Format code
format:
	uv run ruff format .

# Build package
build: clean
	uv run hatch build

# Clean build artifacts
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Run pre-release checks
pre-release-check:
	uv run python scripts/pre-release-check.py

# Create a new release (requires VERSION environment variable)
release:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION not set. Use: make release VERSION=x.x.x"; \
		exit 1; \
	fi
	uv run python scripts/pre-release-check.py
	uv run python scripts/release.py $(VERSION)

# Development workflow helpers
dev-setup: install
	@echo "Development environment ready!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make coverage' to check coverage"
	@echo "Run 'make lint' to check code quality"

# Quick quality check (fast feedback for development)
check: lint test
	@echo "Quick quality checks passed!"
# Makefile for atadata-cli

.PHONY: help install install-dev test test-cov lint format clean build dist upload

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install the package with development dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=atadata_cli --cov-report=html --cov-report=term

lint:  ## Run linting
	flake8 atadata_cli/ tests/
	mypy atadata_cli/

format:  ## Format code
	black atadata_cli/ tests/ sample_script.py

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean  ## Build the package
	python setup.py sdist bdist_wheel

dist: build  ## Create distribution packages
	@echo "Distribution packages created in dist/"

upload: dist  ## Upload to PyPI (requires twine)
	twine upload dist/*

upload-test: dist  ## Upload to Test PyPI (requires twine)
	twine upload --repository testpypi dist/*

check-package: dist  ## Check package before upload
	twine check dist/*

publish: clean build check-package  ## Full publish process (build + check)
	@echo "Package ready for upload!"
	@echo "Run 'make upload' to upload to PyPI"
	@echo "Or 'make upload-test' to test on Test PyPI first"

sample:  ## Run the sample script
	python sample_script.py --dry-run

sample-live:  ## Run the sample script with live API calls
	python sample_script.py

check: lint test  ## Run all checks (lint + test)

all: clean install-dev test-cov  ## Run full development setup

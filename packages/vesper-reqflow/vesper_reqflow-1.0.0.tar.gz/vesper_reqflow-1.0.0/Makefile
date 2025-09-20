# Makefile for API Tester CLI

.PHONY: help install test test-unit test-integration test-cli test-all test-coverage lint format type-check security clean docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install       - Install dependencies"
	@echo "  test          - Run all tests"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-cli      - Run CLI tests only"
	@echo "  test-coverage - Run tests with coverage"
	@echo "  test-fast     - Run tests excluding slow ones"
	@echo "  lint          - Run linting checks"
	@echo "  format        - Format code"
	@echo "  format-check  - Check code formatting"
	@echo "  type-check    - Run type checking"
	@echo "  security      - Run security checks"
	@echo "  all-checks    - Run all quality checks"
	@echo "  clean         - Clean up generated files"
	@echo "  docs          - Generate documentation"

# Installation
install:
	pip install -e .
	pip install -r requirements-dev.txt

# Testing
test:
	python run_tests.py --type all

test-unit:
	python run_tests.py --type unit

test-integration:
	python run_tests.py --type integration

test-cli:
	python run_tests.py --type cli

test-coverage:
	python run_tests.py --type all --coverage

test-fast:
	python run_tests.py --type all --fast

test-parallel:
	python run_tests.py --type all --parallel

# Code quality
lint:
	python run_tests.py --linting

format:
	python -m black src/ tests/
	python -m isort src/ tests/

format-check:
	python run_tests.py --format-check

type-check:
	python run_tests.py --type-check

security:
	python run_tests.py --security

all-checks:
	python run_tests.py --all-checks

# Specific test commands
pytest-unit:
	python -m pytest -m unit -v

pytest-integration:
	python -m pytest -m integration -v

pytest-cli:
	python -m pytest -m cli -v

pytest-ai:
	python -m pytest -m ai -v

pytest-redis:
	python -m pytest -m redis -v

pytest-slow:
	python -m pytest -m slow -v

# Coverage
coverage:
	python -m pytest --cov=src/apitester --cov-report=html --cov-report=term-missing

coverage-xml:
	python -m pytest --cov=src/apitester --cov-report=xml

# Linting tools
flake8:
	python -m flake8 src/ tests/

pylint:
	python -m pylint src/apitester/

black:
	python -m black src/ tests/

black-check:
	python -m black --check --diff src/ tests/

isort:
	python -m isort src/ tests/

isort-check:
	python -m isort --check-only --diff src/ tests/

mypy:
	python -m mypy src/apitester/

bandit:
	python -m bandit -r src/

safety:
	python -m safety check

# Development
dev-install:
	pip install -e ".[dev]"

dev-setup: dev-install
	pre-commit install

# Clean up
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Documentation
docs:
	cd docs && make html

docs-serve:
	cd docs/_build/html && python -m http.server 8000

# Docker
docker-build:
	docker build -t apitester-cli .

docker-test:
	docker run --rm apitester-cli python run_tests.py

# CI/CD helpers
ci-test:
	python run_tests.py --all-checks --coverage --parallel

ci-install:
	pip install -e .
	pip install -r requirements-dev.txt

# Performance testing
perf-test:
	python -m pytest -m "not slow" --benchmark-only

# Database setup (for integration tests)
redis-start:
	docker run -d --name redis-test -p 6379:6379 redis:alpine

redis-stop:
	docker stop redis-test && docker rm redis-test

# Release helpers
version-bump-patch:
	bump2version patch

version-bump-minor:
	bump2version minor

version-bump-major:
	bump2version major

build:
	python -m build

upload-test:
	python -m twine upload --repository testpypi dist/*

upload:
	python -m twine upload dist/*

# Git hooks
pre-commit:
	pre-commit run --all-files

# IDE helpers
vscode-setup:
	mkdir -p .vscode
	echo '{"python.defaultInterpreterPath": "./venv/bin/python", "python.testing.pytestEnabled": true}' > .vscode/settings.json
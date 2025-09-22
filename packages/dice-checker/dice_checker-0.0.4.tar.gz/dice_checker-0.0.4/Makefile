# Makefile for easy development workflows.
# See development.md for docs.
# Note GitHub Actions call uv directly, not this Makefile.

.DEFAULT_GOAL := default

.PHONY: default install lint test upgrade build clean agent-rules

default: agent-rules install lint test

install:
	@uv sync --all-extras
	@uv run pre-commit install

lint:
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uvx pre-commit run -a
	# @echo "🚀 Static type checking: Running mypy"
	# @uvx mypy
	@echo "🚀 Static type checking: Running basedpyright"
	@uvx basedpyright
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uvx deptry src

test:
	@uv run pytest --mpl -vv --cov --cov-config=pyproject.toml --cov-report=xml --cov-report=term --cov-report=html

generate_test_baselines:
	@uv run pytest --mpl-generate-path=tests/baseline

upgrade:
	uv sync --upgrade --all-extras --dev

build:
	uv build

check_readme:
	@uv run python -m doctest -v README.md

clean:
	-rm -rf dist/
	-rm -rf *.egg-info/
	-rm -rf .pytest_cache/
	-rm -rf .mypy_cache/
	-rm -rf .venv/
	-find . -type d -name "__pycache__" -exec rm -rf {} +

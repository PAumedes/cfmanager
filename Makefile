# CFManager — Developer Makefile
# Usage: make <target>  (run `make help` to list all targets)

.DEFAULT_GOAL := help
.PHONY: help dev test test-cov lint format run tui build build-nuitka clean push tag release version check

# ── Config ────────────────────────────────────────────────────────────────────

# Auto-detect version from source
VERSION := $(shell grep '__version__' src/cfmanager/__init__.py | grep -oP '"\K[^"]+')
REMOTE   := origin
BRANCH   := main

# ── Help ──────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "  CFManager v$(VERSION) — available targets"
	@echo ""
	@echo "  Setup"
	@echo "    make dev          Install all dependencies (uv sync --dev)"
	@echo ""
	@echo "  Development"
	@echo "    make run ARGS=''  Run cfm with optional args  e.g. make run ARGS='zones list'"
	@echo "    make tui          Launch the TUI dashboard"
	@echo "    make test         Run test suite"
	@echo "    make test-cov     Run tests with coverage report"
	@echo "    make lint         Check code with ruff"
	@echo "    make format       Auto-fix lint issues with ruff"
	@echo ""
	@echo "  Build"
	@echo "    make build        Build TUI+CLI binary with PyInstaller  → dist/cfm"
	@echo "    make build-nuitka Build CLI-only binary with Nuitka      → dist/cfm-cli"
	@echo "    make clean        Remove build artifacts (dist/, build/)"
	@echo ""
	@echo "  Release"
	@echo "    make push                    Push current branch to $(REMOTE)"
	@echo "    make tag VERSION=v1.2.3      Create + push a git tag"
	@echo "    make release VERSION=v1.2.3  Test → push → tag  (triggers GitHub Actions)"
	@echo "    make version                 Print current version"
	@echo ""

# ── Setup ─────────────────────────────────────────────────────────────────────

dev:
	uv sync --dev

# ── Development ───────────────────────────────────────────────────────────────

run:
	uv run cfm $(ARGS)

tui:
	uv run cfm tui

test:
	uv run pytest tests/ -v --tb=short

test-cov:
	uv run pytest tests/ --cov=cfmanager --cov-report=term-missing

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/

# ── Build ─────────────────────────────────────────────────────────────────────

build:
	uv pip install pyinstaller
	uv run python scripts/build_exe.py

build-nuitka:
	uv pip install nuitka ordered-set
	uv run python scripts/build_exe.py --nuitka

clean:
	rm -rf dist/ build/ *.spec
	rm -rf cfm.build cfm.dist cfm.onefile-build cfm-cli.build cfm-cli.dist

# ── Release ───────────────────────────────────────────────────────────────────

push:
	git push $(REMOTE) $(BRANCH)

# Usage: make tag VERSION=v0.2.0
tag:
	@if [ -z "$(VERSION)" ]; then echo "Usage: make tag VERSION=v1.2.3"; exit 1; fi
	git tag $(VERSION)
	git push $(REMOTE) $(VERSION)
	@echo "Tagged $(VERSION) and pushed. GitHub Actions will build binaries."

# Full release: run tests, push code, create + push tag
# Usage: make release VERSION=v0.2.0
release: check push tag
	@echo ""
	@echo "  Release $(VERSION) in flight."
	@echo "  Watch the build at: https://github.com/PAumedes/cfmanager/actions"
	@echo ""

# Verify tests pass before releasing
check:
	@echo "Running tests before release..."
	uv run pytest tests/ -q --tb=short
	@echo "Tests passed."

version:
	@echo $(VERSION)

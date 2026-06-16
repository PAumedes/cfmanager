# CFManager — Developer Makefile
# Usage: make <target>  (run `make help` to list all targets)

.DEFAULT_GOAL := help
.PHONY: help dev test test-cov lint format run tui build build-nuitka clean push version \
        release major minor patch

# ── Config ────────────────────────────────────────────────────────────────────

VERSION := $(shell grep '__version__' src/cfmanager/__init__.py | grep -oP '"\K[^"]+')
REMOTE  := origin
BRANCH  := main

# Capture the bump type when passed as a positional word after "release"
# e.g. "make release minor" → BUMP_TYPE=minor
BUMP_TYPE := $(word 2, $(MAKECMDGOALS))
ifeq ($(BUMP_TYPE),)
BUMP_TYPE := patch
endif

# ── Help ──────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "  CFManager v$(VERSION) — available targets"
	@echo ""
	@echo "  Setup"
	@echo "    make dev           Install all dependencies (uv sync --dev)"
	@echo ""
	@echo "  Development"
	@echo "    make run ARGS=''   Run cfm with optional args  e.g. make run ARGS='zones list'"
	@echo "    make tui           Launch the TUI dashboard"
	@echo "    make test          Run test suite"
	@echo "    make test-cov      Run tests with coverage report"
	@echo "    make lint          Check code with ruff"
	@echo "    make format        Auto-fix lint issues with ruff"
	@echo ""
	@echo "  Build"
	@echo "    make build         Build TUI+CLI binary with PyInstaller  → dist/cfm"
	@echo "    make build-nuitka  Build CLI-only binary with Nuitka      → dist/cfm-cli"
	@echo "    make clean         Remove build artifacts (dist/, build/)"
	@echo ""
	@echo "  Release  (bumps version, updates CHANGELOG, commits, tags, pushes)"
	@echo "    make release         → patch bump  $(VERSION) → next patch"
	@echo "    make release patch   → patch bump  0.1.1 → 0.1.2"
	@echo "    make release minor   → minor bump  0.1.1 → 0.2.0"
	@echo "    make release major   → major bump  0.1.1 → 1.0.0"
	@echo ""
	@echo "    make push            Push current branch without releasing"
	@echo "    make version         Print current version"
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

version:
	@echo $(VERSION)

# make release [major|minor|patch]
# The script handles: tests → version bump → CHANGELOG → commit → tag → push
release:
	uv run python scripts/release.py $(BUMP_TYPE)

# No-op targets so make doesn't error on "make release minor"
major minor patch:
	@:

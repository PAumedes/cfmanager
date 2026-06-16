# CFManager

A CLI & TUI for managing Cloudflare infrastructure

[Installation](#installation) • [Quick Start](#quick-start) • [CLI Usage](#cli-usage) • [TUI](#tui) • [Configuration](#configuration) • [Development](#development)

[![Tests](https://github.com/PAumedes/cfmanager/actions/workflows/test.yml/badge.svg)](https://github.com/PAumedes/cfmanager/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

---

CFManager (`cfm`) is a terminal-based Cloudflare management tool that provides both a **rich interactive TUI dashboard** (powered by [Textual](https://textual.textualize.io/)) and a **scriptable CLI** (powered by [Typer](https://typer.tiangolo.com/)). Manage your DNS records, domains, SSL certificates, R2 storage, Pages deployments, and load balancers — all without leaving your terminal.

## Features

| Feature | CLI | TUI |
| ------- | :-: | :-: |
| **Zone/Domain Management** | ✅ | ✅ |
| **DNS Record CRUD** | ✅ | ✅ |
| **SSL/TLS Settings** | ✅ | ✅ |
| **R2 Storage Buckets & Objects** | ✅ | ✅ |
| **Pages Projects & Deployments** | ✅ | ✅ |
| **Load Balancers & Pools** | ✅ | ✅ |
| **Multiple Output Formats** (table/json/csv) | ✅ | — |
| **Command Palette** (Ctrl+P) | — | ✅ |
| **Inline Editing** | — | ✅ |
| **Real-time Status Indicators** | — | ✅ |

> **TUI Dashboard** — Cloudflare-branded dark theme with sidebar navigation, filterable data tables, modal dialogs, and keyboard-driven workflows.

## Installation

### Pre-built binary (recommended for non-Python users)

Download the latest binary from [GitHub Releases](https://github.com/PAumedes/cfmanager/releases):

**Linux / macOS:**

```bash
chmod +x cfm-linux-amd64   # or cfm-darwin-amd64
sudo mv cfm-linux-amd64 /usr/local/bin/cfm
cfm --help
```

**Windows:**

Download `cfm.exe` — no Python required. Double-click to open the TUI, or run from PowerShell/Command Prompt for CLI usage.

### uv tool (recommended for Python users)

```bash
uv tool install cfmanager
cfm --help
```

### pip

```bash
pip install cfmanager
```

### From source

```bash
git clone https://github.com/PAumedes/cfmanager.git
cd cfmanager
uv sync
uv run cfm --help
```

## Quick Start

```bash
# Set your Cloudflare API token (stored in ~/.cfmanager/.env)
cfm config set-token YOUR_TOKEN_HERE

# Verify connection
cfm zones list

# Launch TUI
cfm tui
```

The token can also be set via environment variable:

```bash
export CLOUDFLARE_API_TOKEN=your_token_here
```

## CLI Usage

`cfm` follows a `cfm <resource> <action>` pattern. All commands support `--output json` and `--output csv` for scripting.

### Global Options

```bash
cfm --help              # Show all commands
cfm --version           # Show version
cfm -v <command>        # Verbose mode (debug logging)
cfm -o json <command>   # JSON output
cfm -o csv <command>    # CSV output
```

### Zones / Domains

```bash
cfm zones list
cfm zones list --name "example.com"
cfm zones get <zone-id>
cfm zones delete <zone-id>
cfm zones purge-cache <zone-id> --all
cfm zones purge-cache <zone-id> --files "https://example.com/style.css"
```

### DNS Records

```bash
cfm dns list <zone-id>
cfm dns list <zone-id> --type A

cfm dns create <zone-id> \
  --name "api" --type A --content "192.0.2.1" --ttl 3600 --proxied

cfm dns edit <zone-id> <record-id> --content "192.0.2.2" --ttl 1800
cfm dns delete <zone-id> <record-id> --yes
```

### SSL/TLS

```bash
cfm ssl status <zone-id>
cfm ssl set <zone-id> --mode strict   # off | flexible | full | strict
cfm ssl certs <zone-id>
```

### R2 Storage

```bash
cfm r2 list
cfm r2 create --name "my-assets" --location-hint weur
cfm r2 usage my-assets
cfm r2 delete my-assets --yes

cfm r2 objects list my-assets
cfm r2 objects upload my-assets /path/to/file.jpg file.jpg
cfm r2 objects delete my-assets file.jpg
```

> R2 object operations require `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY` — see [Configuration](#configuration).

### Pages

```bash
cfm pages list
cfm pages get my-site
cfm pages deployments my-site
cfm pages rollback my-site <deployment-id>
```

### Load Balancers

```bash
cfm lb list <zone-id>
cfm lb create <zone-id> --name "api-lb" --pools <pool-id-1>,<pool-id-2>
cfm lb edit <zone-id> <lb-id> --enabled
cfm lb edit <zone-id> <lb-id> --disabled
cfm lb pools list
cfm lb pools health <pool-id>
cfm lb delete <zone-id> <lb-id> --yes
```

### Config

```bash
cfm config set-token TOKEN   # Save token to ~/.cfmanager/.env
cfm config show              # Show current config (token masked)
cfm config path              # Show config file location
```

## TUI

Launch with `cfm tui` (or just double-click the binary — no arguments opens the TUI automatically).

If no token is configured, a setup dialog is shown on first launch.

### Navigation

| Key | Action |
| --- | ------ |
| `Ctrl+P` | Command palette |
| `Ctrl+B` | Toggle sidebar |
| `↑/↓` | Navigate lists |
| `Enter` | Select / open details |
| `a` | Add new record/bucket |
| `e` | Edit selected item |
| `d` | Delete selected item |
| `b` / `Esc` | Go back (multi-level screens) |
| `q` | Quit |

### Theme

CFManager uses a custom dark theme inspired by Cloudflare's brand:

- **Background**: Deep navy (`#1a1a2e`)
- **Accent**: Cloudflare orange (`#F6821F`)

## Configuration

### Token lookup order

Token resolution (last one wins):

1. `~/.cfmanager/.env` (set via `cfm config set-token`)
2. `.env` in the current working directory
3. `CLOUDFLARE_API_TOKEN` environment variable ← always wins if set

### Environment Variables

| Variable | Required | Description |
| -------- | :------: | ----------- |
| `CLOUDFLARE_API_TOKEN` | Yes | Your Cloudflare API token |
| `R2_ACCESS_KEY_ID` | R2 objects only | R2-specific access key (from Cloudflare dashboard) |
| `R2_SECRET_ACCESS_KEY` | R2 objects only | R2-specific secret key |
| `CFM_LOG_LEVEL` | No | `DEBUG`, `INFO` (default), `WARNING`, `ERROR` |
| `CFM_LOG_FILE` | No | Log file path (default: `~/.cfmanager/cfmanager.log`) |

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### API Token Permissions

Create your token at [Cloudflare Dashboard → API Tokens](https://dash.cloudflare.com/profile/api-tokens):

| Feature | Required Permissions |
| ------- | -------------------- |
| Zones / DNS | Zone: Read, DNS: Edit |
| SSL/TLS | SSL and Certificates: Edit |
| R2 | Workers R2 Storage: Edit |
| Pages | Cloudflare Pages: Edit |
| Load Balancers | Load Balancers: Edit |

> **Tip**: Use the "Edit zone DNS" template as a starting point and add permissions as needed.

## Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

```bash
git clone https://github.com/PAumedes/cfmanager.git
cd cfmanager
make dev      # uv sync --dev
```

### Makefile reference

```text
make help          Show all targets

# Development
make run ARGS=''   Run cfm — e.g. make run ARGS='zones list'
make tui           Launch the TUI dashboard
make test          Run test suite
make test-cov      Run tests with coverage report
make lint          Check code with ruff
make format        Auto-fix lint issues with ruff

# Build
make build         Build TUI+CLI binary with PyInstaller  → dist/cfm
make build-nuitka  Build CLI-only binary with Nuitka      → dist/cfm-cli
make clean         Remove build artifacts (dist/, build/)

# Release
make release         Bump minor version, update CHANGELOG, commit, tag, push
make release patch   Patch bump  (0.2.0 → 0.2.1)
make release minor   Minor bump  (0.2.0 → 0.3.0)
make release major   Major bump  (0.2.0 → 1.0.0)

# Git
make push          Push current branch to origin
make version       Print current version
```

### Testing

```bash
make test                                        # all tests
make test-cov                                    # with coverage report
uv run pytest tests/test_services/ -v           # services only
uv run pytest tests/test_cli/ -v                # CLI only
```

### Release workflow

```bash
make release          # minor bump (default)
make release patch    # patch bump
make release major    # major bump
```

`make release` runs tests, bumps the version in `__init__.py`, prepends a dated entry to `CHANGELOG.md`, commits, tags, and pushes. GitHub Actions then builds binaries for Linux, macOS, and Windows automatically.

## Architecture

```
cfm (entry point)
 ├── CLI Layer (Typer)        → scriptable commands, table/JSON/CSV output
 ├── TUI Layer (Textual)      → interactive dashboard, keyboard-driven
 ├── Service Layer            → business logic & validation (cloudflare SDK + boto3)
 ├── Core                     → client, config, logging, output formatting
 └── Cloudflare API
```

Key design principles:
- **Separation of concerns**: CLI and TUI are thin layers over shared services
- **Async-ready**: TUI uses `AsyncCloudflare` for non-blocking API calls
- **Testable**: All services accept a client parameter for easy mocking
- **Extensible**: New features follow the same pattern — service → CLI command → TUI screen

## Roadmap

- [x] Phase 1: Core foundation + Zones + DNS (CLI & TUI)
- [x] Phase 2: SSL/TLS + R2 Storage + Pages (CLI & TUI)
- [x] Phase 3: Load Balancers + Windows .exe + Command Palette
- [ ] Future: Multi-account profiles, Workers management, Firewall rules

## Contributing

Contributions are welcome. Open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Run tests (`make test`)
4. Commit your changes
5. Open a Pull Request

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with
  <a href="https://textual.textualize.io/">Textual</a>,
  <a href="https://typer.tiangolo.com/">Typer</a>, and the
  <a href="https://github.com/cloudflare/cloudflare-python">Cloudflare Python SDK</a>
</p>

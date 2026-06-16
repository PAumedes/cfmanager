# CFManager

A CLI & TUI for managing Cloudflare infrastructure

[Installation](#installation) • [Quick Start](#quick-start) • [CLI Usage](#cli-usage) • [TUI](#tui) • [Configuration](#configuration)

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

### TUI Dashboard

> A Cloudflare-branded dark theme with sidebar navigation, filterable data tables, modal dialogs, and keyboard-driven workflows.

## Installation

### Pre-built binary (recommended for non-Python users)

Download the latest binary from [GitHub Releases](https://github.com/PAumedes/cfmanager/releases), then:

**Linux / macOS:**

```bash
chmod +x cfm-linux-amd64   # or cfm-darwin-amd64
sudo mv cfm-linux-amd64 /usr/local/bin/cfm
cfm --help
```

**Windows:**

Download `cfm.exe` — no Python required. Run it directly from PowerShell or Command Prompt.

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
# List all zones
cfm zones list

# Filter by name
cfm zones list --name "example.com"

# Get zone details
cfm zones get <zone-id>

# Delete a zone (with confirmation)
cfm zones delete <zone-id>

# Purge all cache
cfm zones purge-cache <zone-id> --all

# Purge specific files
cfm zones purge-cache <zone-id> --files "https://example.com/style.css,https://example.com/app.js"
```

### DNS Records

```bash
# List all DNS records for a zone
cfm dns list <zone-id>

# Filter by type
cfm dns list <zone-id> --type A

# Create a new record
cfm dns create <zone-id> \
  --name "api" \
  --type A \
  --content "192.0.2.1" \
  --ttl 3600 \
  --proxied

# Edit a record
cfm dns edit <zone-id> <record-id> \
  --content "192.0.2.2" \
  --ttl 1800

# Delete a record
cfm dns delete <zone-id> <record-id> --yes
```

### SSL/TLS

```bash
# View SSL status for a zone
cfm ssl status <zone-id>

# Change SSL mode
cfm ssl set <zone-id> --mode strict

# List certificate packs
cfm ssl certs <zone-id>
```

### R2 Storage (Buckets & Objects)

```bash
# List all R2 buckets
cfm r2 list

# Create a new bucket
cfm r2 create --name "my-assets" --location-hint weur

# View bucket usage stats
cfm r2 usage my-assets

# Delete a bucket
cfm r2 delete my-assets --yes

# List objects inside a bucket
cfm r2 objects list my-assets

# Upload an object
cfm r2 objects upload my-assets /path/to/file.jpg file.jpg

# Delete an object
cfm r2 objects delete my-assets file.jpg
```

### Pages

```bash
# List all Pages projects
cfm pages list

# View project details
cfm pages get my-site

# List deployments
cfm pages deployments my-site

# Rollback to a previous deployment
cfm pages rollback my-site <deployment-id>
```

### Load Balancers

```bash
# List load balancers for a zone
cfm lb list <zone-id>

# Create a load balancer
cfm lb create <zone-id> \
  --name "api-lb" \
  --pools <pool-id-1>,<pool-id-2>

# Toggle load balancer
cfm lb edit <zone-id> <lb-id> --enabled
cfm lb edit <zone-id> <lb-id> --disabled

# List pools and health
cfm lb pools list
cfm lb pools health <pool-id>

# Delete a load balancer
cfm lb delete <zone-id> <lb-id> --yes
```

## TUI

Launch the interactive TUI with:

```bash
cfm tui
```

### Navigation

| Key | Action |
| --- | ------ |
| `Ctrl+P` | Command palette |
| `Ctrl+B` | Toggle sidebar |
| `↑/↓` or `j/k` | Navigate lists |
| `Enter` | Select / Open details |
| `a` | Add new record/bucket/project |
| `e` | Edit selected record |
| `d` | Delete selected record/bucket/project |
| `/` | Filter current table |
| `?` | Show keyboard shortcuts |
| `q` | Quit |

### Theme

CFManager uses a custom dark theme inspired by Cloudflare's brand:

- **Background**: Deep navy (`#1a1a2e`)
- **Accent**: Cloudflare orange (`#F6821F`)
- **Status colors**: Active / Pending / Error

## Configuration

### Token setup

```bash
cfm config set-token TOKEN   # Save token to ~/.cfmanager/.env
cfm config show              # Show current config (token masked)
cfm config path              # Show config file location
```

Token lookup order:

1. `CLOUDFLARE_API_TOKEN` environment variable
2. `.env` in the current directory
3. `~/.cfmanager/.env` (set via `cfm config set-token`)

### Environment Variables

| Variable | Required | Description |
| -------- | -------- | ----------- |
| `CLOUDFLARE_API_TOKEN` | Yes | Your Cloudflare API token |
| `CFM_LOG_LEVEL` | No | Log level: `DEBUG`, `INFO` (default), `WARNING`, `ERROR` |
| `CFM_LOG_FILE` | No | Log file path (default: `~/.cfmanager/cfmanager.log`) |

### API Token Permissions

Create your token at [Cloudflare Dashboard → API Tokens](https://dash.cloudflare.com/profile/api-tokens) with these permissions:

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

### Setup & common tasks

```bash
make dev       # Install dependencies
make test      # Run tests
make build     # Build executable (PyInstaller)
make release VERSION=v0.2.0  # Tag + push release
```

Running individual commands:

```bash
uv run cfm zones list
uv run cfm tui
```

### Testing

```bash
# Run all tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=cfmanager --cov-report=term-missing

# Specific suite
uv run pytest tests/test_services/ -v
uv run pytest tests/test_cli/ -v
uv run pytest tests/test_tui/ -v
```

## Architecture

```
cfm (entry point)
 ├── CLI Layer (Typer)        → Human-friendly commands
 ├── TUI Layer (Textual)      → Interactive dashboard
 ├── Service Layer             → Business logic & validation (uses cloudflare + boto3)
 ├── Core                      → Client, config, logging, output
 └── Cloudflare API
```

Key design principles:
- **Separation of concerns**: CLI and TUI are thin layers over shared services
- **Async-ready**: TUI uses `AsyncCloudflare` for non-blocking API calls
- **Testable**: All services accept a client parameter for easy mocking
- **Extensible**: New services follow the same pattern — add service → CLI command → TUI screen

## Roadmap

- [x] Phase 1: Core foundation + Zones + DNS (CLI & TUI)
- [x] Phase 2: SSL/TLS + R2 Storage + Pages (CLI & TUI)
- [x] Phase 3: Load Balancers + Windows .exe + Command Palette
- [ ] Future: Multi-account profiles, Workers management, Firewall rules

## Contributing

Contributions are welcome. Open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Run tests (`uv run pytest`)
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

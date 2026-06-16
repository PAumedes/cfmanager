<p align="center">
  <h1 align="center">☁️ CFManager</h1>
  <p align="center">
    <strong>A powerful CLI & TUI for managing Cloudflare infrastructure</strong>
  </p>
  <p align="center">
    <a href="#installation">Installation</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#cli-usage">CLI Usage</a> •
    <a href="#tui-dashboard">TUI Dashboard</a> •
    <a href="#configuration">Configuration</a>
  </p>
</p>

---

CFManager (`cfm`) is a terminal-based Cloudflare management tool that provides both a **rich interactive TUI dashboard** (powered by [Textual](https://textual.textualize.io/)) and a **scriptable CLI** (powered by [Typer](https://typer.tiangolo.com/)). Manage your DNS records, domains, SSL certificates, R2 storage, Pages deployments, and load balancers — all without leaving your terminal.

## ✨ Features

| Feature | CLI | TUI |
|---------|:---:|:---:|
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

### 🎨 TUI Dashboard

> A Cloudflare-branded dark theme with sidebar navigation, filterable data tables, modal dialogs, and keyboard-driven workflows.

<!-- Screenshots will be added after implementation -->

## 📦 Installation

### From GitHub Releases (Recommended)

Download the latest pre-built binary for your platform from [Releases](https://github.com/yourusername/cfmanager/releases):

- **Windows**: `cfm.exe` — standalone executable, no Python required
- **Linux**: `cfm-linux-amd64`
- **macOS**: `cfm-darwin-amd64`

### From PyPI

```bash
pip install cfmanager
# or with uv
uv tool install cfmanager
```

### From Source

```bash
git clone https://github.com/yourusername/cfmanager.git
cd cfmanager
uv sync
```

## 🚀 Quick Start

### 1. Set up your API Token

Create a [Cloudflare API Token](https://dash.cloudflare.com/profile/api-tokens) with the permissions you need, then:

```bash
# Option 1: Environment variable
export CLOUDFLARE_API_TOKEN="your_token_here"

# Option 2: .env file in your working directory
echo "CLOUDFLARE_API_TOKEN=your_token_here" > .env
```

*Note: Account ID is automatically detected from the token at startup.*

### 2. Verify connection

```bash
cfm zones list
```

### 3. Launch the TUI

```bash
cfm tui
```

## 💻 CLI Usage

CFManager follows a `cfm <resource> <action>` pattern. All commands support `--output json` and `--output csv` for scripting.

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

## 🖥️ TUI Dashboard

Launch the interactive TUI with:

```bash
cfm tui
```

### Navigation

| Key | Action |
|-----|--------|
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
- **Status colors**: 🟢 Active / 🟡 Pending / 🔴 Error

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CLOUDFLARE_API_TOKEN` | ✅ | Your Cloudflare API token |
| `CFM_LOG_LEVEL` | ❌ | Log level: `DEBUG`, `INFO` (default), `WARNING`, `ERROR` |
| `CFM_LOG_FILE` | ❌ | Log file path (default: `~/.cfmanager/cfmanager.log`) |

### .env File

Create a `.env` file in your working directory or home directory:

```env
CLOUDFLARE_API_TOKEN=your_token_here
CFM_LOG_LEVEL=INFO
```

### API Token Permissions

Create your token at [Cloudflare Dashboard → API Tokens](https://dash.cloudflare.com/profile/api-tokens) with these permissions:

| Feature | Required Permissions |
|---------|---------------------|
| Zones / DNS | Zone: Read, DNS: Edit |
| SSL/TLS | SSL and Certificates: Edit |
| R2 | Workers R2 Storage: Edit |
| Pages | Cloudflare Pages: Edit |
| Load Balancers | Load Balancers: Edit |

> **Tip**: Use the "Edit zone DNS" template as a starting point and add permissions as needed.

## 🛠️ Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

```bash
git clone https://github.com/yourusername/cfmanager.git
cd cfmanager
uv sync --dev
```

### Running

```bash
# CLI
uv run cfm zones list

# TUI
uv run cfm tui

# TUI with hot-reload (dev mode)
uv run textual run --dev src/cfmanager/tui/app.py
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

### Building the Windows Executable

```bash
uv run python scripts/build_exe.py
# Output: dist/cfm.exe
```

## 🏗️ Architecture

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

## 🗺️ Roadmap

- [x] **Phase 1**: Core foundation + Zones + DNS (CLI & TUI)
- [ ] **Phase 2**: SSL/TLS + R2 Storage (with Objects) + Pages
- [ ] **Phase 3**: Load Balancers + Windows .exe + Polish
- [ ] **Future**: Multi-account profiles, Workers management, Firewall rules

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Run tests (`uv run pytest`)
4. Commit your changes
5. Open a Pull Request

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ using
  <a href="https://textual.textualize.io/">Textual</a>,
  <a href="https://typer.tiangolo.com/">Typer</a>, and the
  <a href="https://github.com/cloudflare/cloudflare-python">Cloudflare Python SDK</a>
</p>

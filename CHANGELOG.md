# Changelog

All notable changes to CFManager are documented here.
Format: `## [version] - YYYY-MM-DD` followed by commits included in that release.

---

## [0.1.1] - 2026-06-16

- Fix exe: default to TUI on double-click, show setup dialog if no token
- ci: opt into Node.js 24 across all workflows
- Fix release workflow: remove PyPI job, add separate publish-pypi.yml
- Add Makefile, cfm config command, updated docs, and PyPI metadata

## [0.1.0] - 2026-06-16

- Initial release: full CFManager implementation (all 3 phases)
- Core infrastructure: CloudflareClient, Config, Logger, OutputFormatter
- Services: zones, dns, ssl, r2, pages, load balancers (sync + async)
- CLI (cfm): all subcommands — zones, dns, ssl, r2, pages, lb, config
- TUI: Textual dashboard with sidebar, 6 feature screens, Ctrl+P command palette
- Build: PyInstaller (TUI+CLI) + Nuitka (CLI-only) scripts
- CI/CD: GitHub Actions for test, release (3-platform binaries), Nuitka build

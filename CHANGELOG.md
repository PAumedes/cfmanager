# Changelog

All notable changes to CFManager are documented here.

---

## [0.4.0] - 2026-06-17

- feat: TUI improvements and code review fixes
- fix: resolve all ruff lint violations exposed by removing || true

## [0.3.0] - 2026-06-16

- fix: apply code review findings and add comprehensive test coverage
- docs: rewrite README to match current Makefile and feature set
- chore: remove internal planning and debug artifacts
- fix: prevent CHANGELOG corruption when prepending new releases

## [0.2.0] - 2026-06-16

- docs: fix release.py docstring to reflect minor as default
- chore: change default release bump from patch to minor
- Add CHANGELOG.md, scripts/release.py, and smart make release
- Fix exe: default to TUI on double-click, show setup dialog if no token
- ci: opt into Node.js 24 across all workflows
- Fix release workflow: remove PyPI job, add separate publish-pypi.yml

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

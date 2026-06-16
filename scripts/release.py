#!/usr/bin/env python3
"""Bump version, generate changelog entry, commit, tag, and push.

Usage:
    python scripts/release.py         # 0.1.1 → 0.2.0  (default: minor)
    python scripts/release.py minor   # 0.1.1 → 0.2.0
    python scripts/release.py patch   # 0.1.1 → 0.1.2
    python scripts/release.py major   # 0.1.1 → 1.0.0
"""

import re
import sys
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
INIT_FILE = ROOT / "src" / "cfmanager" / "__init__.py"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"


# ── Version helpers ────────────────────────────────────────────────────────────

def read_version() -> tuple[int, int, int]:
    text = INIT_FILE.read_text()
    m = re.search(r'__version__\s*=\s*"(\d+)\.(\d+)\.(\d+)"', text)
    if not m:
        raise SystemExit("Could not find __version__ in src/cfmanager/__init__.py")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def bump(current: tuple[int, int, int], kind: str) -> tuple[int, int, int]:
    major, minor, patch = current
    if kind == "major":
        return major + 1, 0, 0
    if kind == "minor":
        return major, minor + 1, 0
    if kind == "patch":
        return major, minor, patch + 1
    raise SystemExit(f"Unknown bump type '{kind}'. Use: major | minor | patch")


def write_version(version: str) -> None:
    text = INIT_FILE.read_text()
    text = re.sub(r'__version__\s*=\s*"[^"]+"', f'__version__ = "{version}"', text)
    INIT_FILE.write_text(text)


# ── Git helpers ────────────────────────────────────────────────────────────────

def git(*args, check=True) -> str:
    result = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(f"git {' '.join(args)} failed (exit {result.returncode})")
    return result.stdout.strip()


def last_tag() -> str | None:
    out = git("describe", "--tags", "--abbrev=0", check=False)
    return out if out else None


def commits_since(tag: str | None) -> list[str]:
    ref = f"{tag}..HEAD" if tag else "HEAD"
    out = git("log", ref, "--oneline", "--no-merges")
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    # Strip the 7-char hash prefix
    return [l[8:].strip() for l in lines if len(l) > 8]


# ── Changelog ─────────────────────────────────────────────────────────────────

def make_entry(version: str, messages: list[str]) -> str:
    today = date.today().strftime("%Y-%m-%d")
    lines = [f"## [{version}] - {today}", ""]
    for msg in messages:
        lines.append(f"- {msg}")
    if not messages:
        lines.append("- Minor improvements and fixes")
    lines.append("")
    return "\n".join(lines)


def prepend_changelog(entry: str) -> None:
    if CHANGELOG_FILE.exists():
        existing = CHANGELOG_FILE.read_text()
        # Match only a section header at the start of a line (avoids hitting inline examples)
        marker = "\n## ["
        if marker in existing:
            idx = existing.index(marker) + 1  # keep the leading newline, insert after it
            content = existing[:idx] + entry + "\n" + existing[idx:]
        else:
            content = existing.rstrip() + "\n\n" + entry
    else:
        content = "# Changelog\n\nAll notable changes to CFManager are documented here.\n\n---\n\n" + entry
    CHANGELOG_FILE.write_text(content)


# ── Tests ─────────────────────────────────────────────────────────────────────

def run_tests() -> None:
    print("Running tests...")
    import os
    result = subprocess.run(
        ["uv", "run", "--frozen", "pytest", "tests/", "-q", "--tb=short"],
        cwd=ROOT,
        env={**os.environ, "UV_PROJECT_ENVIRONMENT": os.environ.get("UV_PROJECT_ENVIRONMENT", "")},
    )
    if result.returncode != 0:
        raise SystemExit("Tests failed. Release aborted.")
    print("Tests passed.\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    kind = sys.argv[1].lower() if len(sys.argv) > 1 else "minor"

    current = read_version()
    new_tuple = bump(current, kind)
    new_version = ".".join(str(x) for x in new_tuple)
    tag = f"v{new_version}"
    prev = ".".join(str(x) for x in current)

    print(f"  Version : {prev} → {new_version}  ({kind} bump)")

    prev_tag = last_tag()
    messages = commits_since(prev_tag)
    print(f"  Commits : {len(messages)} since {prev_tag or 'beginning'}")
    for m in messages:
        print(f"            · {m}")
    print()

    # Confirm before proceeding
    answer = input(f"Release {tag}? [y/N] ").strip().lower()
    if answer != "y":
        raise SystemExit("Aborted.")

    run_tests()

    # Update files
    write_version(new_version)
    entry = make_entry(new_version, messages)
    prepend_changelog(entry)

    print(f"Updated {INIT_FILE.name} and CHANGELOG.md\n")
    print("Changelog entry:")
    print(entry)

    # Commit + tag + push
    git("add", str(INIT_FILE), str(CHANGELOG_FILE))
    git("commit", "-m", f"chore: release {tag}")
    git("tag", tag)
    git("push", "origin", "main")
    git("push", "origin", tag)

    print(f"Done. {tag} is live.")
    print(f"Watch builds: https://github.com/PAumedes/cfmanager/actions")


if __name__ == "__main__":
    main()

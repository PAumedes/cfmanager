#!/usr/bin/env python3
"""Build standalone cfm executable.

Usage:
    python scripts/build_exe.py              # PyInstaller (TUI + CLI)
    python scripts/build_exe.py --nuitka     # Nuitka (CLI-only, smaller + faster)
"""

import subprocess
import sys
import shutil
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent


def build_pyinstaller():
    """Full TUI + CLI build via PyInstaller."""
    if shutil.which("pyinstaller") is None:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    theme_src = ROOT / "src" / "cfmanager" / "tui" / "theme.tcss"
    sep = ";" if sys.platform == "win32" else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "cfm",
        # Collect all Textual internals (CSS, fonts, icons) automatically
        "--collect-data", "textual",
        # Hidden imports for dynamic plugin loading
        "--hidden-import=textual",
        "--hidden-import=textual.app",
        "--hidden-import=textual.widgets",
        "--hidden-import=textual.widget",
        "--hidden-import=textual.screen",
        "--hidden-import=textual.command",
        "--hidden-import=cloudflare",
        "--hidden-import=boto3",
        "--hidden-import=botocore",
        "--hidden-import=dotenv",
        "--hidden-import=typer",
        "--hidden-import=rich",
    ]

    # Bundle our theme.tcss
    if theme_src.exists():
        cmd += [f"--add-data={theme_src}{sep}cfmanager/tui"]

    # Optional icon
    for candidate in [ROOT / "assets" / "icon.ico", ROOT / "icon.ico"]:
        if candidate.exists():
            cmd += [f"--icon={candidate}"]
            break

    cmd.append(str(ROOT / "src" / "cfmanager" / "__main__.py"))

    print(f"Building with PyInstaller (TUI + CLI)...")
    _run(cmd)

    exe = "cfm.exe" if sys.platform == "win32" else "cfm"
    _report(ROOT / "dist" / exe)


def build_nuitka():
    """CLI-only build via Nuitka — smaller binary, faster startup, no TUI."""
    try:
        import nuitka  # noqa: F401
    except ImportError:
        print("Installing Nuitka...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "nuitka", "ordered-set"])

    exe_name = "cfm-cli.exe" if sys.platform == "win32" else "cfm-cli"

    cmd = [
        sys.executable, "-m", "nuitka",
        "--onefile",
        f"--output-filename={exe_name}",
        "--output-dir=dist",
        # Include cfmanager + runtime deps
        "--include-package=cfmanager",
        "--include-package=cloudflare",
        "--include-package=typer",
        "--include-package=rich",
        "--include-package=dotenv",
        # Exclude TUI and heavy optional deps to keep binary small
        "--nofollow-import-to=textual",
        "--nofollow-import-to=boto3",
        "--nofollow-import-to=botocore",
        # Python compatibility
        "--python-flag=no_site",
        str(ROOT / "src" / "cfmanager" / "__main__.py"),
    ]

    print("Building with Nuitka (CLI-only, no TUI)...")
    print("Note: first run compiles C code, takes 2-5 minutes.")
    _run(cmd)

    _report(ROOT / "dist" / exe_name)


def _run(cmd):
    print(" ".join(str(c) for c in cmd))
    print()
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as e:
        print(f"\nBuild FAILED (exit {e.returncode})", file=sys.stderr)
        sys.exit(e.returncode)


def _report(path: Path):
    if path.exists():
        size_mb = path.stat().st_size / 1_048_576
        print(f"\nBuild succeeded — {path} ({size_mb:.1f} MB)")
    else:
        print(f"\nBuild may have succeeded but {path} not found. Check dist/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build cfm executable")
    parser.add_argument("--nuitka", action="store_true", help="Use Nuitka (CLI-only, smaller/faster)")
    args = parser.parse_args()

    if args.nuitka:
        build_nuitka()
    else:
        build_pyinstaller()

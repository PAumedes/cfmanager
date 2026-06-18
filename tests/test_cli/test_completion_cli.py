"""Tests for cfm completion sub-command."""
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from cfmanager.cli.app import app

runner = CliRunner()


def test_completion_install_calls_typer(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    with patch("cfmanager.cli.completion.install_shell_completion") as mock_install:
        result = runner.invoke(app, ["completion", "install"], catch_exceptions=False)
    assert result.exit_code == 0


def test_completion_show_prints_script(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    with patch("cfmanager.cli.completion.show_shell_completion") as mock_show:
        result = runner.invoke(app, ["completion", "show"], catch_exceptions=False)
    assert result.exit_code == 0

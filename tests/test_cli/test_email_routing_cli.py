"""Tests for cfm email CLI commands."""
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from cfmanager.cli.app import app

runner = CliRunner()
_PATCH_VALIDATE = patch("cfmanager.core.config.Config.validate")
_PATCH_CLIENT = lambda c: patch("cfmanager.core.client.CloudflareClient", return_value=c)


def _mock_client():
    c = MagicMock()
    c.api_token = "tok"
    c.sync_client = MagicMock()
    c.get_account_id.return_value = "acc1"
    return c


def test_email_status(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    status = {"enabled": True, "name": "Email Routing", "tag": "email_routing", "modified_on": "2024-01-01"}
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.email_routing.EmailRoutingService.get_status", return_value=status),
    ):
        result = runner.invoke(app, ["email", "status", "zone_abc"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "True" in result.output or "enabled" in result.output.lower()


def test_email_rules(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    rules = [{"id": "r1", "name": "Admins", "enabled": True, "priority": 1, "matchers": "to=admin@example.com", "actions": "forward:dest@example.com"}]
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.email_routing.EmailRoutingService.list_rules", return_value=rules),
    ):
        result = runner.invoke(app, ["email", "rules", "zone_abc"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "Admins" in result.output


def test_email_addresses(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    addresses = [{"id": "a1", "email": "dest@example.com", "verified": "2024-01-01"}]
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.email_routing.EmailRoutingService.list_addresses", return_value=addresses),
    ):
        result = runner.invoke(app, ["email", "addresses"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "dest@example.com" in result.output


def test_email_enable(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.email_routing.EmailRoutingService.enable", return_value={"enabled": True}) as mock_en,
    ):
        result = runner.invoke(app, ["email", "enable", "zone_abc"], catch_exceptions=False)
    assert result.exit_code == 0
    mock_en.assert_called_once_with("zone_abc")

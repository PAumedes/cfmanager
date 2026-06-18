"""Tests for cfm firewall CLI commands."""
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
    return c


def test_firewall_rules_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    rules = [{"id": "r1", "mode": "block", "target": "ip", "value": "1.2.3.4", "notes": ""}]
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.firewall.FirewallService.list_access_rules", return_value=rules),
    ):
        result = runner.invoke(app, ["firewall", "rules", "zone_abc"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "1.2.3.4" in result.output


def test_firewall_rules_create(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    created = {"id": "r2", "mode": "block", "target": "ip", "value": "9.9.9.9", "notes": ""}
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.firewall.FirewallService.create_access_rule", return_value=created) as mock_create,
    ):
        result = runner.invoke(
            app,
            ["firewall", "rules-create", "zone_abc", "--mode", "block", "--target", "ip", "--value", "9.9.9.9"],
            catch_exceptions=False,
        )
    assert result.exit_code == 0
    mock_create.assert_called_once_with("zone_abc", mode="block", target="ip", value="9.9.9.9", notes="")


def test_firewall_rules_delete(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.firewall.FirewallService.delete_access_rule", return_value="r1") as mock_del,
    ):
        result = runner.invoke(app, ["firewall", "rules-delete", "zone_abc", "r1", "--yes"], catch_exceptions=False)
    assert result.exit_code == 0
    mock_del.assert_called_once_with("zone_abc", "r1")


def test_firewall_waf_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    packages = [{"id": "p1", "name": "OWASP", "description": "OWASP rules", "detection_mode": "traditional"}]
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.firewall.FirewallService.list_waf_packages", return_value=packages),
    ):
        result = runner.invoke(app, ["firewall", "waf", "zone_abc"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "OWASP" in result.output

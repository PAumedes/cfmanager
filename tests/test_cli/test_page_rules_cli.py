"""Tests for cfm pagerules CLI commands."""
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


_RULES = [{"id": "pr1", "status": "active", "target": "example.com/*", "actions": "always_use_https"}]


def test_pagerules_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.page_rules.PageRulesService.list_page_rules", return_value=_RULES),
    ):
        result = runner.invoke(app, ["pagerules", "list", "zone_abc"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "example.com/*" in result.output


def test_pagerules_delete(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.page_rules.PageRulesService.delete_page_rule", return_value="pr1") as mock_del,
    ):
        result = runner.invoke(app, ["pagerules", "delete", "zone_abc", "pr1", "--yes"], catch_exceptions=False)
    assert result.exit_code == 0
    mock_del.assert_called_once_with("zone_abc", "pr1")

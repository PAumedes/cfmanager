"""Tests for cfm tunnels CLI commands."""
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


_TUNNELS = [{"id": "t1", "name": "my-tunnel", "status": "healthy", "created_at": "2024-01-01", "remote_config": True}]


def test_tunnels_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.tunnels.TunnelsService.list_tunnels", return_value=_TUNNELS),
    ):
        result = runner.invoke(app, ["tunnels", "list"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "my-tunnel" in result.output


def test_tunnels_get(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.tunnels.TunnelsService.get_tunnel", return_value=_TUNNELS[0]) as mock_get,
    ):
        result = runner.invoke(app, ["tunnels", "get", "t1"], catch_exceptions=False)
    assert result.exit_code == 0
    mock_get.assert_called_once_with("t1")

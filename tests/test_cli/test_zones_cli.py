import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from cfmanager.cli.app import app

runner = CliRunner()


def _make_mock_client():
    """Return a mock CloudflareClient suitable for CLI injection."""
    client = MagicMock()
    client.api_token = "test_token"
    client.sync_client = MagicMock()
    client.async_client = MagicMock()
    client.get_account_id.return_value = "mock_account_id"
    return client


def test_zones_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")

    mock_client = _make_mock_client()

    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.zones.ZoneService.list_zones",
            return_value=[
                {
                    "id": "zone_abc",
                    "name": "example.com",
                    "status": "active",
                    "paused": False,
                    "type": "full",
                    "development_mode": 0,
                }
            ],
        ),
    ):
        result = runner.invoke(app, ["zones", "list"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "example.com" in result.output


def test_zones_list_empty(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")

    mock_client = _make_mock_client()

    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.zones.ZoneService.list_zones",
            return_value=[],
        ),
    ):
        result = runner.invoke(app, ["zones", "list"], catch_exceptions=False)

    assert result.exit_code == 0


def test_dns_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")

    mock_client = _make_mock_client()

    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.dns.DNSService.list_dns_records",
            return_value=[
                {
                    "id": "rec_1",
                    "name": "api.example.com",
                    "type": "A",
                    "content": "1.2.3.4",
                    "ttl": 3600,
                    "proxied": True,
                }
            ],
        ),
    ):
        result = runner.invoke(
            app, ["dns", "list", "zone_abc"], catch_exceptions=False
        )

    assert result.exit_code == 0
    assert "api.example.com" in result.output

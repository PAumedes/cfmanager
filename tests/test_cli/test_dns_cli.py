from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from cfmanager.cli.app import app
from cfmanager.core.exceptions import APIError

runner = CliRunner()


def _make_mock_client():
    client = MagicMock()
    client.api_token = "test_token"
    client.sync_client = MagicMock()
    client.async_client = MagicMock()
    client.get_account_id.return_value = "mock_account_id"
    return client


def test_dns_list(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.dns.DNSService.list_dns_records",
            return_value=[
                {"id": "rec_1", "name": "api.example.com", "type": "A",
                 "content": "1.2.3.4", "ttl": 3600, "proxied": True}
            ],
        ),
    ):
        result = runner.invoke(app, ["dns", "list", "zone_abc"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "api.example.com" in result.output


def test_dns_list_empty(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch("cfmanager.services.dns.DNSService.list_dns_records", return_value=[]),
    ):
        result = runner.invoke(app, ["dns", "list", "zone_abc"], catch_exceptions=False)

    assert result.exit_code == 0


def test_dns_create(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.dns.DNSService.create_dns_record",
            return_value={"id": "rec_new", "name": "api.example.com"},
        ),
    ):
        result = runner.invoke(
            app,
            ["dns", "create", "zone_abc",
             "--name", "api.example.com",
             "--type", "A",
             "--content", "1.2.3.4"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    assert "rec_new" in result.output


def test_dns_edit(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.dns.DNSService.edit_dns_record",
            return_value={"id": "rec_1", "name": "api.example.com"},
        ),
    ):
        result = runner.invoke(
            app,
            ["dns", "edit", "zone_abc", "rec_1", "--content", "5.6.7.8"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    assert "rec_1" in result.output


def test_dns_delete(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch("cfmanager.services.dns.DNSService.delete_dns_record"),
    ):
        result = runner.invoke(
            app, ["dns", "delete", "zone_abc", "rec_1", "--yes"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    assert "rec_1" in result.output


def test_dns_list_api_error(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.dns.DNSService.list_dns_records",
            side_effect=APIError("network failure"),
        ),
    ):
        result = runner.invoke(app, ["dns", "list", "zone_abc"])

    assert result.exit_code == 1
    assert "Error" in result.output

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


_MOCK_SSL_SETTING = {
    "zone_id": "zone_abc",
    "mode": "flexible",
    "enabled_protocols": [],
    "certificate_packs": [
        {"id": "pack_1", "type": "universal", "status": "active", "hosts": ["example.com"]}
    ],
}


def test_ssl_status_shows_mode(monkeypatch):
    # Verifies fix 1.2: output reads 'mode' key, not 'value'
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.ssl.SSLService.get_ssl_setting",
            return_value=_MOCK_SSL_SETTING,
        ),
    ):
        result = runner.invoke(app, ["ssl", "status", "zone_abc"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "flexible" in result.output
    assert "SSL Mode: unknown" not in result.output


def test_ssl_status_shows_cert_packs(monkeypatch):
    # Verifies fix 1.2: reads 'certificate_packs' key, not 'cert_packs'
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.ssl.SSLService.get_ssl_setting",
            return_value=_MOCK_SSL_SETTING,
        ),
    ):
        result = runner.invoke(app, ["ssl", "status", "zone_abc"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "No certificate packs found." not in result.output
    assert "pack_1" in result.output


def test_ssl_status_no_certs(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    setting = {**_MOCK_SSL_SETTING, "certificate_packs": []}
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch("cfmanager.services.ssl.SSLService.get_ssl_setting", return_value=setting),
    ):
        result = runner.invoke(app, ["ssl", "status", "zone_abc"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "No certificate packs found." in result.output


def test_ssl_set(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.ssl.SSLService.set_ssl_mode",
            return_value={"zone_id": "zone_abc", "mode": "full"},
        ),
    ):
        result = runner.invoke(
            app, ["ssl", "set", "zone_abc", "--mode", "full"], catch_exceptions=False
        )

    assert result.exit_code == 0
    assert "full" in result.output


def test_ssl_set_invalid_mode(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
    ):
        result = runner.invoke(app, ["ssl", "set", "zone_abc", "--mode", "bogus"])

    assert result.exit_code == 1
    assert "Invalid mode" in result.output


def test_ssl_certs(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.ssl.SSLService.list_cert_packs",
            return_value=[
                {"id": "pack_1", "type": "universal", "status": "active", "hosts": ["example.com"]}
            ],
        ),
    ):
        result = runner.invoke(app, ["ssl", "certs", "zone_abc"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "pack_1" in result.output


def test_ssl_status_api_error(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        patch("cfmanager.core.config.Config.validate"),
        patch("cfmanager.core.client.CloudflareClient", return_value=mock_client),
        patch(
            "cfmanager.services.ssl.SSLService.get_ssl_setting",
            side_effect=APIError("ssl fetch failed"),
        ),
    ):
        result = runner.invoke(app, ["ssl", "status", "zone_abc"])

    assert result.exit_code == 1
    assert "Error" in result.output

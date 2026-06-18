import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from cfmanager.cli.app import app

runner = CliRunner()


def _make_mock_client():
    client = MagicMock()
    client.api_token = "test_token"
    client.sync_client = MagicMock()
    client.async_client = MagicMock()
    client.get_account_id.return_value = "mock_account_id"
    return client


_PATCH_VALIDATE = patch("cfmanager.core.config.Config.validate")
_PATCH_CLIENT = lambda c: patch("cfmanager.core.client.CloudflareClient", return_value=c)


# ── export ────────────────────────────────────────────────────────────────────

def test_dns_export_prints_csv_to_stdout(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    csv_output = "name,type,content,ttl,proxied,comment\napi.example.com,A,1.2.3.4,3600,False,\n"
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        patch("cfmanager.services.dns.DNSService.export_records", return_value=csv_output),
    ):
        result = runner.invoke(app, ["dns", "export", "zone_abc"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "api.example.com" in result.output


def test_dns_export_writes_to_file(monkeypatch, tmp_path):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    csv_output = "name,type,content,ttl,proxied,comment\napi.example.com,A,1.2.3.4,3600,False,\n"
    out_file = str(tmp_path / "records.csv")
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        patch("cfmanager.services.dns.DNSService.export_records", return_value=csv_output),
    ):
        result = runner.invoke(app, ["dns", "export", "zone_abc", "--output", out_file], catch_exceptions=False)

    assert result.exit_code == 0
    assert Path(out_file).read_text() == csv_output


def test_dns_export_bind_format(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    bind_output = "api.example.com 3600 IN A 1.2.3.4\n"
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        patch("cfmanager.services.dns.DNSService.export_records", return_value=bind_output) as mock_export,
    ):
        result = runner.invoke(app, ["dns", "export", "zone_abc", "--format", "bind"], catch_exceptions=False)

    assert result.exit_code == 0
    mock_export.assert_called_once_with("zone_abc", format="bind")


# ── import ────────────────────────────────────────────────────────────────────

_CSV = "name,type,content,ttl,proxied,comment\napi.example.com,A,1.2.3.4,3600,false,\n"


def test_dns_import_dry_run_shows_records(monkeypatch, tmp_path):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    csv_file = tmp_path / "records.csv"
    csv_file.write_text(_CSV)
    parsed = [{"name": "api.example.com", "type": "A", "content": "1.2.3.4", "ttl": 3600, "proxied": False, "comment": ""}]
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        patch("cfmanager.services.dns.DNSService.import_records", return_value=parsed),
    ):
        result = runner.invoke(app, ["dns", "import", "zone_abc", "--file", str(csv_file), "--dry-run"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Dry run" in result.output or "dry" in result.output.lower()
    assert "1" in result.output


def test_dns_import_creates_records(monkeypatch, tmp_path):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    csv_file = tmp_path / "records.csv"
    csv_file.write_text(_CSV)
    created = [{"id": "r1", "name": "api.example.com", "type": "A", "content": "1.2.3.4", "ttl": 3600, "proxied": False}]
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        patch("cfmanager.services.dns.DNSService.import_records", return_value=created) as mock_import,
    ):
        result = runner.invoke(app, ["dns", "import", "zone_abc", "--file", str(csv_file)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "1" in result.output
    mock_import.assert_called_once_with("zone_abc", _CSV, format="csv", dry_run=False)


def test_dns_import_missing_file_exits_with_error(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
    ):
        result = runner.invoke(app, ["dns", "import", "zone_abc", "--file", "/no/such/file.csv"])

    assert result.exit_code != 0


# ── find ──────────────────────────────────────────────────────────────────────

def test_dns_find_across_zones(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    zones = [{"id": "z1", "name": "example.com"}]
    found = [{"id": "r1", "name": "api.example.com", "type": "A", "content": "1.2.3.4", "ttl": 3600, "proxied": False, "zone_id": "z1", "zone_name": "example.com"}]
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        patch("cfmanager.services.zones.ZoneService.list_zones", return_value=zones),
        patch("cfmanager.services.dns.DNSService.find_records_across_zones", return_value=found),
    ):
        result = runner.invoke(app, ["dns", "find", "api.example.com"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "api.example.com" in result.output


def test_dns_find_no_results(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        patch("cfmanager.services.zones.ZoneService.list_zones", return_value=[]),
        patch("cfmanager.services.dns.DNSService.find_records_across_zones", return_value=[]),
    ):
        result = runner.invoke(app, ["dns", "find", "nobody.example.com"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "No records" in result.output or result.output.strip() == "" or "0" in result.output

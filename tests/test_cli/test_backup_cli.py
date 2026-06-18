import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from cfmanager.cli.app import app

runner = CliRunner()

_BACKUP_DATA = {
    "version": 1,
    "zone_id": "z1",
    "zone_name": "example.com",
    "dns_records": [
        {"id": "r1", "name": "api.example.com", "type": "A", "content": "1.2.3.4", "ttl": 3600, "proxied": False, "comment": ""},
    ],
    "ssl": {"mode": "full"},
}


def _make_mock_client():
    client = MagicMock()
    client.api_token = "test_token"
    client.sync_client = MagicMock()
    client.async_client = MagicMock()
    client.get_account_id.return_value = "mock_account_id"
    return client


_PATCH_VALIDATE = patch("cfmanager.core.config.Config.validate")
_PATCH_CLIENT = lambda c: patch("cfmanager.core.client.CloudflareClient", return_value=c)


# ── backup ────────────────────────────────────────────────────────────────────

def test_zones_backup_prints_json_to_stdout(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        patch("cfmanager.services.backup.BackupService.backup_zone", return_value=_BACKUP_DATA),
    ):
        result = runner.invoke(app, ["zones", "backup", "z1"], catch_exceptions=False)

    assert result.exit_code == 0
    # Strip any leading dev/log lines before the JSON object
    json_start = result.output.find("{")
    data = json.loads(result.output[json_start:])
    assert data["zone_name"] == "example.com"


def test_zones_backup_writes_to_file(monkeypatch, tmp_path):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    out_file = str(tmp_path / "backup.json")
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        patch("cfmanager.services.backup.BackupService.backup_zone", return_value=_BACKUP_DATA),
    ):
        result = runner.invoke(app, ["zones", "backup", "z1", "--output", out_file], catch_exceptions=False)

    assert result.exit_code == 0
    saved = json.loads(Path(out_file).read_text())
    assert saved["zone_id"] == "z1"


def test_zones_backup_yaml_format(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        patch("cfmanager.services.backup.BackupService.backup_zone", return_value=_BACKUP_DATA),
    ):
        result = runner.invoke(app, ["zones", "backup", "z1", "--format", "yaml"], catch_exceptions=False)

    assert result.exit_code == 0
    # YAML output should contain the zone name without JSON braces
    assert "zone_name" in result.output
    assert "example.com" in result.output


# ── restore ───────────────────────────────────────────────────────────────────

def test_zones_restore_from_json_file(monkeypatch, tmp_path):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    backup_file = tmp_path / "backup.json"
    backup_file.write_text(json.dumps(_BACKUP_DATA))
    restore_result = {"dns_created": 1, "ssl_set": True}
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        patch("cfmanager.services.backup.BackupService.restore_zone", return_value=restore_result),
    ):
        result = runner.invoke(app, ["zones", "restore", "z1", "--file", str(backup_file)], catch_exceptions=False)

    assert result.exit_code == 0
    assert "1" in result.output


def test_zones_restore_dry_run(monkeypatch, tmp_path):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    backup_file = tmp_path / "backup.json"
    backup_file.write_text(json.dumps(_BACKUP_DATA))
    restore_result = {"dns_created": 1, "ssl_set": True}
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        patch("cfmanager.services.backup.BackupService.restore_zone", return_value=restore_result) as mock_restore,
    ):
        result = runner.invoke(app, ["zones", "restore", "z1", "--file", str(backup_file), "--dry-run"], catch_exceptions=False)

    assert result.exit_code == 0
    mock_restore.assert_called_once_with("z1", _BACKUP_DATA, dry_run=True)


def test_zones_restore_missing_file_exits_with_error(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
    ):
        result = runner.invoke(app, ["zones", "restore", "z1", "--file", "/no/such/backup.json"])

    assert result.exit_code != 0

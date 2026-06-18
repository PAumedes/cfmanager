"""Tests for the typed-name confirmation guard on zone delete (§7.15)."""
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


_ZONE = {"id": "zone_abc", "name": "example.com", "status": "active", "paused": False, "type": "full", "development_mode": 0, "name_servers": [], "original_name_servers": []}

_PATCH_VALIDATE = patch("cfmanager.core.config.Config.validate")
_PATCH_CLIENT = lambda c: patch("cfmanager.core.client.CloudflareClient", return_value=c)
_PATCH_GET_ZONE = lambda: patch("cfmanager.services.zones.ZoneService.get_zone", return_value=_ZONE)
_PATCH_DELETE = lambda: patch("cfmanager.services.zones.ZoneService.delete_zone")


def test_delete_zone_with_correct_confirm_name_succeeds(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        _PATCH_GET_ZONE(),
        _PATCH_DELETE() as mock_delete,
    ):
        result = runner.invoke(
            app,
            ["zones", "delete", "zone_abc", "--confirm-name", "example.com"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    mock_delete.assert_called_once_with("zone_abc")


def test_delete_zone_with_wrong_confirm_name_aborts(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        _PATCH_GET_ZONE(),
        _PATCH_DELETE() as mock_delete,
    ):
        result = runner.invoke(
            app,
            ["zones", "delete", "zone_abc", "--confirm-name", "wrong.com"],
        )

    assert result.exit_code != 0 or "abort" in result.output.lower() or "match" in result.output.lower()
    mock_delete.assert_not_called()


def test_delete_zone_force_bypasses_confirmation(monkeypatch):
    """--yes skips both interactive prompt and typed-name check."""
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        _PATCH_DELETE() as mock_delete,
    ):
        result = runner.invoke(
            app,
            ["zones", "delete", "zone_abc", "--yes"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    mock_delete.assert_called_once_with("zone_abc")


def test_delete_zone_confirm_name_requires_zone_name_lookup(monkeypatch):
    """When --confirm-name is given, the zone name must be fetched to compare."""
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test_token")
    mock_client = _make_mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mock_client),
        _PATCH_GET_ZONE() as mock_get,
        _PATCH_DELETE(),
    ):
        runner.invoke(
            app,
            ["zones", "delete", "zone_abc", "--confirm-name", "example.com"],
            catch_exceptions=False,
        )

    mock_get.assert_called_once_with("zone_abc")

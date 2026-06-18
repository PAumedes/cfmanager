"""Tests for --watch flag on zones list and dns list."""
import time
from unittest.mock import MagicMock, patch, call
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


_ZONES = [{"id": "z1", "name": "example.com", "status": "active", "paused": False, "type": "full"}]
_RECORDS = [{"id": "r1", "name": "api.example.com", "type": "A", "content": "1.2.3.4", "ttl": 3600, "proxied": False}]


def test_zones_list_no_watch_no_sleep(monkeypatch):
    """Without --watch, zones list exits immediately."""
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.zones.ZoneService.list_zones", return_value=_ZONES),
        patch("time.sleep") as mock_sleep,
    ):
        result = runner.invoke(app, ["zones", "list"], catch_exceptions=False)
    assert result.exit_code == 0
    mock_sleep.assert_not_called()


def test_zones_list_watch_calls_list_multiple_times(monkeypatch):
    """With --watch N, zones list repeats N+1 iterations and then exits (simulated)."""
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    call_count = [0]

    def list_side_effect(name=None):
        call_count[0] += 1
        if call_count[0] > 2:
            raise KeyboardInterrupt
        return _ZONES

    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.zones.ZoneService.list_zones", side_effect=list_side_effect),
        patch("time.sleep"),
    ):
        result = runner.invoke(app, ["zones", "list", "--watch", "1"])

    assert call_count[0] >= 2


def test_dns_list_watch_calls_list_multiple_times(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    call_count = [0]

    def list_side_effect(zone_id, name=None, type=None):
        call_count[0] += 1
        if call_count[0] > 2:
            raise KeyboardInterrupt
        return _RECORDS

    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.dns.DNSService.list_dns_records", side_effect=list_side_effect),
        patch("time.sleep"),
    ):
        result = runner.invoke(app, ["dns", "list", "zone_abc", "--watch", "1"])

    assert call_count[0] >= 2

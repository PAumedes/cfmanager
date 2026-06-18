"""Tests for cfm analytics CLI commands."""
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


def test_analytics_r2(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    summary = {
        "bucket_count": 2,
        "buckets": [
            {"name": "assets", "location": "enam", "created": "2024-01-01"},
            {"name": "logs", "location": "weur", "created": "2024-02-01"},
        ],
    }
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.analytics.AnalyticsService.r2_usage_summary", return_value=summary),
    ):
        result = runner.invoke(app, ["analytics", "r2"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "assets" in result.output
    assert "2" in result.output


def test_analytics_zones(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok")
    mc = _mock_client()
    summary = {
        "total_zones": 3,
        "active": 2,
        "paused": 1,
        "zones": [
            {"id": "z1", "name": "example.com", "status": "active", "paused": False},
        ],
    }
    with (
        _PATCH_VALIDATE,
        _PATCH_CLIENT(mc),
        patch("cfmanager.services.analytics.AnalyticsService.zone_summary", return_value=summary),
    ):
        result = runner.invoke(app, ["analytics", "zones"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "3" in result.output

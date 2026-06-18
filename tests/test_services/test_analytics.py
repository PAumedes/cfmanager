"""Tests for AnalyticsService."""
from unittest.mock import MagicMock, patch
from cfmanager.services.analytics import AnalyticsService


def test_r2_usage_summary(mock_cloudflare_client):
    service = AnalyticsService(mock_cloudflare_client)
    mock_cloudflare_client.get_account_id.return_value = "acc1"

    b1 = MagicMock()
    b1.name = "bucket-a"
    b1.creation_date = "2024-01-01"
    b1.location = "enam"
    b2 = MagicMock()
    b2.name = "bucket-b"
    b2.creation_date = "2024-02-01"
    b2.location = "weur"

    buckets_result = MagicMock()
    buckets_result.buckets = [b1, b2]
    mock_cloudflare_client.sync_client.r2.buckets.list.return_value = buckets_result

    result = service.r2_usage_summary()

    assert result["bucket_count"] == 2
    assert len(result["buckets"]) == 2
    assert result["buckets"][0]["name"] == "bucket-a"


def test_r2_usage_summary_empty(mock_cloudflare_client):
    service = AnalyticsService(mock_cloudflare_client)
    mock_cloudflare_client.get_account_id.return_value = "acc1"

    empty = MagicMock()
    empty.buckets = []
    mock_cloudflare_client.sync_client.r2.buckets.list.return_value = empty

    result = service.r2_usage_summary()

    assert result["bucket_count"] == 0
    assert result["buckets"] == []


def test_zone_summary(mock_cloudflare_client):
    service = AnalyticsService(mock_cloudflare_client)

    z1 = MagicMock()
    z1.id = "z1"
    z1.name = "example.com"
    z1.status = "active"
    z1.paused = False
    z1.type = "full"
    z1.development_mode = 0
    mock_cloudflare_client.sync_client.zones.list.return_value = [z1]

    result = service.zone_summary()

    assert result["total_zones"] == 1
    assert result["active"] == 1
    assert result["paused"] == 0
    assert len(result["zones"]) == 1
    assert result["zones"][0]["name"] == "example.com"

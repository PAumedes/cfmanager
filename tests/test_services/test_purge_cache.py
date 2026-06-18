import pytest
from unittest.mock import MagicMock
from cfmanager.services.zones import ZoneService
from cfmanager.core.exceptions import ValidationError


def test_purge_by_tags(mock_cloudflare_client):
    service = ZoneService(mock_cloudflare_client)

    result = service.purge_cache("zone_123", tags=["product-images", "homepage"])

    assert result is True
    mock_cloudflare_client.sync_client.zones.purge_cache.assert_called_once_with(
        zone_id="zone_123", tags=["product-images", "homepage"]
    )


def test_purge_by_hosts(mock_cloudflare_client):
    service = ZoneService(mock_cloudflare_client)

    result = service.purge_cache("zone_123", hosts=["assets.example.com"])

    assert result is True
    mock_cloudflare_client.sync_client.zones.purge_cache.assert_called_once_with(
        zone_id="zone_123", hosts=["assets.example.com"]
    )


def test_purge_by_prefixes(mock_cloudflare_client):
    service = ZoneService(mock_cloudflare_client)

    result = service.purge_cache("zone_123", prefixes=["https://example.com/static/"])

    assert result is True
    mock_cloudflare_client.sync_client.zones.purge_cache.assert_called_once_with(
        zone_id="zone_123", prefixes=["https://example.com/static/"]
    )


def test_purge_with_no_targets_raises(mock_cloudflare_client):
    service = ZoneService(mock_cloudflare_client)

    with pytest.raises(ValidationError, match="at least one"):
        service.purge_cache("zone_123")


def test_purge_everything_with_files_raises(mock_cloudflare_client):
    service = ZoneService(mock_cloudflare_client)

    with pytest.raises(ValidationError, match="cannot be combined"):
        service.purge_cache("zone_123", purge_everything=True, files=["https://example.com/a"])


def test_purge_tags_and_hosts_both_sent(mock_cloudflare_client):
    """Multiple targeting modes (excluding purge_everything) should all be forwarded."""
    service = ZoneService(mock_cloudflare_client)

    result = service.purge_cache("zone_123", tags=["t1"], hosts=["h1.example.com"])

    assert result is True
    mock_cloudflare_client.sync_client.zones.purge_cache.assert_called_once_with(
        zone_id="zone_123", tags=["t1"], hosts=["h1.example.com"]
    )


def test_purge_purge_everything_still_works(mock_cloudflare_client):
    service = ZoneService(mock_cloudflare_client)

    result = service.purge_cache("zone_123", purge_everything=True)

    assert result is True
    mock_cloudflare_client.sync_client.zones.purge_cache.assert_called_once_with(
        zone_id="zone_123", purge_everything=True
    )

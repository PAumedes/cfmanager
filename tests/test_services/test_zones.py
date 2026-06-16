import pytest
from unittest.mock import MagicMock, AsyncMock
from cfmanager.services.zones import ZoneService
from cfmanager.core.exceptions import APIError

def test_list_zones(mock_cloudflare_client):
    service = ZoneService(mock_cloudflare_client)
    
    mock_zone = MagicMock()
    mock_zone.id = "zone_123"
    mock_zone.name = "example.com"
    mock_zone.status = "active"
    mock_zone.paused = False
    mock_zone.type = "full"
    mock_zone.development_mode = 0
    
    mock_cloudflare_client.sync_client.zones.list.return_value = [mock_zone]
    
    result = service.list_zones()
    assert len(result) == 1
    assert result[0]["id"] == "zone_123"
    assert result[0]["name"] == "example.com"
    mock_cloudflare_client.sync_client.zones.list.assert_called_once()

def test_get_zone(mock_cloudflare_client):
    service = ZoneService(mock_cloudflare_client)
    
    mock_zone = MagicMock()
    mock_zone.id = "zone_123"
    mock_zone.name = "example.com"
    mock_zone.status = "active"
    mock_zone.paused = False
    mock_zone.type = "full"
    mock_zone.development_mode = 0
    mock_zone.name_servers = ["ns1.cloudflare.com"]
    mock_zone.original_name_servers = ["ns1.olddns.com"]
    
    mock_cloudflare_client.sync_client.zones.get.return_value = mock_zone
    
    result = service.get_zone("zone_123")
    assert result["id"] == "zone_123"
    assert result["name"] == "example.com"
    mock_cloudflare_client.sync_client.zones.get.assert_called_once_with(zone_id="zone_123")

def test_delete_zone(mock_cloudflare_client):
    service = ZoneService(mock_cloudflare_client)
    
    result = service.delete_zone("zone_123")
    assert result == "zone_123"
    mock_cloudflare_client.sync_client.zones.delete.assert_called_once_with(zone_id="zone_123")

def test_purge_cache(mock_cloudflare_client):
    service = ZoneService(mock_cloudflare_client)
    
    assert service.purge_cache("zone_123") is True
    mock_cloudflare_client.sync_client.zones.purge_cache.assert_called_with(zone_id="zone_123", purge_everything=True)
    
    assert service.purge_cache("zone_123", files=["http://example.com/style.css"]) is True
    mock_cloudflare_client.sync_client.zones.purge_cache.assert_called_with(
        zone_id="zone_123", files=["http://example.com/style.css"]
    )

@pytest.mark.asyncio
async def test_list_zones_async(mock_cloudflare_client):
    service = ZoneService(mock_cloudflare_client)
    
    mock_zone = MagicMock()
    mock_zone.id = "zone_123"
    mock_zone.name = "example.com"
    mock_zone.status = "active"
    mock_zone.paused = False
    mock_zone.type = "full"
    mock_zone.development_mode = 0
    
    class AsyncPage:
        def __aiter__(self):
            return self
        async def __anext__(self):
            if not hasattr(self, "_done"):
                self._done = True
                return mock_zone
            raise StopAsyncIteration

    mock_cloudflare_client.async_client.zones.list = AsyncMock(return_value=AsyncPage())
    
    result = await service.list_zones_async()
    assert len(result) == 1
    assert result[0]["id"] == "zone_123"


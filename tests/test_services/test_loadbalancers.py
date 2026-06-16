import pytest
from unittest.mock import MagicMock, AsyncMock
from cfmanager.services.loadbalancers import LoadBalancerService


def test_list_load_balancers(mock_cloudflare_client):
    service = LoadBalancerService(mock_cloudflare_client)

    mock_lb = MagicMock()
    mock_lb.id = "lb_123"
    mock_lb.name = "my-lb.example.com"
    mock_lb.enabled = True
    mock_lb.fallback_pool = "pool_fallback"
    mock_lb.default_pools = ["pool_a", "pool_b"]
    mock_lb.created_on = "2024-01-01T00:00:00Z"

    mock_cloudflare_client.sync_client.load_balancers.list.return_value = [mock_lb]

    result = service.list_load_balancers("zone_123")

    assert len(result) == 1
    assert result[0]["id"] == "lb_123"
    assert result[0]["name"] == "my-lb.example.com"
    assert result[0]["enabled"] is True
    assert result[0]["fallback_pool"] == "pool_fallback"
    assert result[0]["default_pools"] == ["pool_a", "pool_b"]

    mock_cloudflare_client.sync_client.load_balancers.list.assert_called_once_with(
        zone_id="zone_123"
    )


def test_create_load_balancer(mock_cloudflare_client):
    service = LoadBalancerService(mock_cloudflare_client)

    mock_lb = MagicMock()
    mock_lb.id = "lb_new"
    mock_lb.name = "new-lb.example.com"
    mock_lb.enabled = True
    mock_lb.fallback_pool = "pool_fallback"
    mock_lb.default_pools = ["pool_a"]
    mock_lb.created_on = "2024-06-01T00:00:00Z"
    mock_cloudflare_client.sync_client.load_balancers.create.return_value = mock_lb

    result = service.create_load_balancer(
        zone_id="zone_123",
        name="new-lb.example.com",
        default_pools=["pool_a"],
        fallback_pool="pool_fallback",
    )

    assert result["id"] == "lb_new"
    assert result["name"] == "new-lb.example.com"
    assert result["enabled"] is True

    mock_cloudflare_client.sync_client.load_balancers.create.assert_called_once_with(
        zone_id="zone_123",
        name="new-lb.example.com",
        default_pools=["pool_a"],
        fallback_pool="pool_fallback",
        enabled=True,
    )


def test_delete_load_balancer(mock_cloudflare_client):
    service = LoadBalancerService(mock_cloudflare_client)

    result = service.delete_load_balancer("zone_123", "lb_123")

    assert result == "lb_123"
    mock_cloudflare_client.sync_client.load_balancers.delete.assert_called_once_with(
        load_balancer_id="lb_123",
        zone_id="zone_123",
    )


def test_list_pools(mock_cloudflare_client):
    service = LoadBalancerService(mock_cloudflare_client)

    mock_pool = MagicMock()
    mock_pool.id = "pool_a"
    mock_pool.name = "primary-pool"
    mock_pool.enabled = True
    mock_pool.description = "Primary origin pool"
    mock_pool.origins = [{"address": "1.2.3.4", "enabled": True}]

    mock_cloudflare_client.sync_client.load_balancers.pools.list.return_value = [mock_pool]

    result = service.list_pools()

    assert len(result) == 1
    assert result[0]["id"] == "pool_a"
    assert result[0]["name"] == "primary-pool"
    assert result[0]["enabled"] is True

    mock_cloudflare_client.sync_client.load_balancers.pools.list.assert_called_once_with(
        account_id="mock_account_id"
    )


@pytest.mark.asyncio
async def test_list_load_balancers_async(mock_cloudflare_client):
    service = LoadBalancerService(mock_cloudflare_client)

    mock_lb = MagicMock()
    mock_lb.id = "lb_async"
    mock_lb.name = "async-lb.example.com"
    mock_lb.enabled = False
    mock_lb.fallback_pool = "pool_fb"
    mock_lb.default_pools = ["pool_x"]
    mock_lb.created_on = "2024-01-01T00:00:00Z"

    class AsyncPage:
        def __aiter__(self):
            return self

        async def __anext__(self):
            if not hasattr(self, "_done"):
                self._done = True
                return mock_lb
            raise StopAsyncIteration

    mock_cloudflare_client.async_client.load_balancers.list = AsyncMock(
        return_value=AsyncPage()
    )

    result = await service.list_load_balancers_async("zone_123")

    assert len(result) == 1
    assert result[0]["id"] == "lb_async"
    assert result[0]["enabled"] is False

    mock_cloudflare_client.async_client.load_balancers.list.assert_called_once_with(
        zone_id="zone_123"
    )

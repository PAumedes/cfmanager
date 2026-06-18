"""Tests for TunnelsService."""
from unittest.mock import MagicMock
from cfmanager.services.tunnels import TunnelsService


def test_list_tunnels(mock_cloudflare_client):
    service = TunnelsService(mock_cloudflare_client)
    mock_cloudflare_client.get_account_id.return_value = "acc1"

    tunnel = MagicMock()
    tunnel.id = "t1"
    tunnel.name = "my-tunnel"
    tunnel.status = "healthy"
    tunnel.created_at = "2024-01-01T00:00:00Z"
    tunnel.remote_config = True
    mock_cloudflare_client.sync_client.zero_trust.tunnels.list.return_value = [tunnel]

    result = service.list_tunnels()

    assert len(result) == 1
    assert result[0]["id"] == "t1"
    assert result[0]["name"] == "my-tunnel"
    assert result[0]["status"] == "healthy"
    mock_cloudflare_client.sync_client.zero_trust.tunnels.list.assert_called_once_with(
        account_id="acc1"
    )


def test_get_tunnel(mock_cloudflare_client):
    service = TunnelsService(mock_cloudflare_client)
    mock_cloudflare_client.get_account_id.return_value = "acc1"

    tunnel = MagicMock()
    tunnel.id = "t1"
    tunnel.name = "my-tunnel"
    tunnel.status = "healthy"
    tunnel.created_at = "2024-01-01T00:00:00Z"
    tunnel.remote_config = True
    mock_cloudflare_client.sync_client.zero_trust.tunnels.get.return_value = tunnel

    result = service.get_tunnel("t1")

    assert result["id"] == "t1"
    mock_cloudflare_client.sync_client.zero_trust.tunnels.get.assert_called_once_with(
        tunnel_id="t1", account_id="acc1"
    )


def test_list_tunnels_empty(mock_cloudflare_client):
    service = TunnelsService(mock_cloudflare_client)
    mock_cloudflare_client.get_account_id.return_value = "acc1"
    mock_cloudflare_client.sync_client.zero_trust.tunnels.list.return_value = []
    assert service.list_tunnels() == []

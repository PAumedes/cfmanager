import pytest
from unittest.mock import MagicMock, AsyncMock
from cfmanager.services.ssl import SSLService
from cfmanager.core.exceptions import ValidationError


def test_get_ssl_setting(mock_cloudflare_client):
    service = SSLService(mock_cloudflare_client)

    mock_ssl = MagicMock()
    mock_ssl.value = "full"
    mock_ssl.enabled_protocols = ["TLSv1.2", "TLSv1.3"]
    mock_cloudflare_client.sync_client.zones.settings.ssl.get.return_value = mock_ssl

    mock_pack = MagicMock()
    mock_pack.id = "pack_abc"
    mock_pack.type = "universal"
    mock_pack.status = "active"
    mock_pack.hosts = ["*.example.com", "example.com"]
    mock_cloudflare_client.sync_client.ssl.certificate_packs.list.return_value = [mock_pack]

    result = service.get_ssl_setting("zone_123")

    assert result["zone_id"] == "zone_123"
    assert result["mode"] == "full"
    assert result["enabled_protocols"] == ["TLSv1.2", "TLSv1.3"]
    assert len(result["certificate_packs"]) == 1
    assert result["certificate_packs"][0]["id"] == "pack_abc"
    assert result["certificate_packs"][0]["status"] == "active"

    mock_cloudflare_client.sync_client.zones.settings.ssl.get.assert_called_once_with(
        zone_id="zone_123"
    )
    mock_cloudflare_client.sync_client.ssl.certificate_packs.list.assert_called_once_with(
        zone_id="zone_123"
    )


def test_set_ssl_mode(mock_cloudflare_client):
    service = SSLService(mock_cloudflare_client)

    mock_result = MagicMock()
    mock_result.value = "strict"
    mock_cloudflare_client.sync_client.zones.settings.ssl.edit.return_value = mock_result

    result = service.set_ssl_mode("zone_123", "strict")

    assert result["zone_id"] == "zone_123"
    assert result["mode"] == "strict"
    mock_cloudflare_client.sync_client.zones.settings.ssl.edit.assert_called_once_with(
        zone_id="zone_123", value="strict"
    )


def test_set_ssl_mode_invalid(mock_cloudflare_client):
    service = SSLService(mock_cloudflare_client)

    with pytest.raises(ValidationError):
        service.set_ssl_mode("zone_123", "invalid_mode")

    with pytest.raises(ValidationError):
        service.set_ssl_mode("zone_123", "")

    # Valid modes should not raise
    mock_result = MagicMock()
    mock_result.value = "flexible"
    mock_cloudflare_client.sync_client.zones.settings.ssl.edit.return_value = mock_result
    for valid_mode in ("off", "flexible", "full", "strict"):
        result = service.set_ssl_mode("zone_123", valid_mode)
        assert result["zone_id"] == "zone_123"


def test_list_cert_packs(mock_cloudflare_client):
    service = SSLService(mock_cloudflare_client)

    mock_pack1 = MagicMock()
    mock_pack1.id = "pack_1"
    mock_pack1.type = "universal"
    mock_pack1.status = "active"
    mock_pack1.hosts = ["example.com"]
    mock_pack1.primary_certificate = "cert_id_1"

    mock_pack2 = MagicMock()
    mock_pack2.id = "pack_2"
    mock_pack2.type = "advanced"
    mock_pack2.status = "pending_validation"
    mock_pack2.hosts = ["api.example.com"]
    mock_pack2.primary_certificate = None

    mock_cloudflare_client.sync_client.ssl.certificate_packs.list.return_value = [
        mock_pack1,
        mock_pack2,
    ]

    result = service.list_cert_packs("zone_123")

    assert len(result) == 2
    assert result[0]["id"] == "pack_1"
    assert result[0]["type"] == "universal"
    assert result[0]["status"] == "active"
    assert result[0]["primary_certificate"] == "cert_id_1"
    assert result[1]["id"] == "pack_2"
    assert result[1]["status"] == "pending_validation"

    mock_cloudflare_client.sync_client.ssl.certificate_packs.list.assert_called_once_with(
        zone_id="zone_123"
    )


@pytest.mark.asyncio
async def test_get_ssl_setting_async(mock_cloudflare_client):
    service = SSLService(mock_cloudflare_client)

    mock_ssl = MagicMock()
    mock_ssl.value = "full"
    mock_ssl.enabled_protocols = ["TLSv1.3"]
    mock_cloudflare_client.async_client.zones.settings.ssl.get = AsyncMock(
        return_value=mock_ssl
    )

    mock_pack = MagicMock()
    mock_pack.id = "pack_async"
    mock_pack.type = "universal"
    mock_pack.status = "active"
    mock_pack.hosts = ["example.com"]

    class AsyncPage:
        def __aiter__(self):
            return self

        async def __anext__(self):
            if not hasattr(self, "_done"):
                self._done = True
                return mock_pack
            raise StopAsyncIteration

    mock_cloudflare_client.async_client.ssl.certificate_packs.list = AsyncMock(
        return_value=AsyncPage()
    )

    result = await service.get_ssl_setting_async("zone_123")

    assert result["zone_id"] == "zone_123"
    assert result["mode"] == "full"
    assert len(result["certificate_packs"]) == 1
    assert result["certificate_packs"][0]["id"] == "pack_async"

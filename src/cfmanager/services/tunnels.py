from typing import Any, Dict, List

from cfmanager.core.client import CloudflareClient
from cfmanager.core.decorators import cf_api
from cfmanager.core.logger import get_logger

logger = get_logger()


def _serialize_tunnel(t) -> Dict[str, Any]:
    return {
        "id": t.id,
        "name": getattr(t, "name", ""),
        "status": getattr(t, "status", ""),
        "created_at": getattr(t, "created_at", ""),
        "remote_config": getattr(t, "remote_config", False),
    }


class TunnelsService:
    def __init__(self, client: CloudflareClient):
        self.client = client

    @cf_api("listing Cloudflare Tunnels")
    def list_tunnels(self) -> List[Dict[str, Any]]:
        account_id = self.client.get_account_id()
        tunnels = self.client.sync_client.zero_trust.tunnels.list(account_id=account_id)
        return [_serialize_tunnel(t) for t in tunnels]

    @cf_api("getting Cloudflare Tunnel")
    def get_tunnel(self, tunnel_id: str) -> Dict[str, Any]:
        account_id = self.client.get_account_id()
        t = self.client.sync_client.zero_trust.tunnels.get(
            tunnel_id=tunnel_id, account_id=account_id
        )
        return _serialize_tunnel(t)

    @cf_api("listing Cloudflare Tunnels async")
    async def list_tunnels_async(self) -> List[Dict[str, Any]]:
        account_id = self.client.get_account_id()
        page = await self.client.async_client.zero_trust.tunnels.list(account_id=account_id)
        results = []
        async for t in page:
            results.append(_serialize_tunnel(t))
        return results

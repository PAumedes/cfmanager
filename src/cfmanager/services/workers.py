from typing import Any, Dict, List

from cfmanager.core.client import CloudflareClient
from cfmanager.core.decorators import cf_api
from cfmanager.core.logger import get_logger

logger = get_logger()


class WorkersService:
    def __init__(self, client: CloudflareClient):
        self.client = client

    @cf_api("listing Workers scripts")
    def list_workers(self) -> List[Dict[str, Any]]:
        account_id = self.client.get_account_id()
        scripts = self.client.sync_client.workers.scripts.list(account_id=account_id)
        return [
            {
                "id": s.id,
                "etag": getattr(s, "etag", ""),
                "modified_on": getattr(s, "modified_on", ""),
            }
            for s in scripts
        ]

    @cf_api("deleting Worker")
    def delete_worker(self, script_name: str) -> str:
        account_id = self.client.get_account_id()
        self.client.sync_client.workers.scripts.delete(
            script_name=script_name, account_id=account_id
        )
        return script_name

    @cf_api("listing Worker routes")
    def list_routes(self, zone_id: str) -> List[Dict[str, Any]]:
        routes = self.client.sync_client.workers.routes.list(zone_id=zone_id)
        return [
            {
                "id": r.id,
                "pattern": getattr(r, "pattern", ""),
                "script": getattr(r, "script", ""),
            }
            for r in routes
        ]

    @cf_api("listing Workers scripts async")
    async def list_workers_async(self) -> List[Dict[str, Any]]:
        account_id = self.client.get_account_id()
        page = await self.client.async_client.workers.scripts.list(account_id=account_id)
        results = []
        async for s in page:
            results.append(
                {
                    "id": s.id,
                    "etag": getattr(s, "etag", ""),
                    "modified_on": getattr(s, "modified_on", ""),
                }
            )
        return results


class KVService:
    def __init__(self, client: CloudflareClient):
        self.client = client

    @cf_api("listing KV namespaces")
    def list_namespaces(self) -> List[Dict[str, Any]]:
        account_id = self.client.get_account_id()
        namespaces = self.client.sync_client.kv.namespaces.list(account_id=account_id)
        return [{"id": ns.id, "title": getattr(ns, "title", "")} for ns in namespaces]

    @cf_api("creating KV namespace")
    def create_namespace(self, title: str) -> Dict[str, Any]:
        account_id = self.client.get_account_id()
        ns = self.client.sync_client.kv.namespaces.create(
            account_id=account_id, title=title
        )
        return {"id": ns.id, "title": getattr(ns, "title", title)}

    @cf_api("deleting KV namespace")
    def delete_namespace(self, namespace_id: str) -> str:
        account_id = self.client.get_account_id()
        self.client.sync_client.kv.namespaces.delete(
            namespace_id=namespace_id, account_id=account_id
        )
        return namespace_id

    @cf_api("listing KV namespaces async")
    async def list_namespaces_async(self) -> List[Dict[str, Any]]:
        account_id = self.client.get_account_id()
        page = await self.client.async_client.kv.namespaces.list(account_id=account_id)
        results = []
        async for ns in page:
            results.append({"id": ns.id, "title": getattr(ns, "title", "")})
        return results

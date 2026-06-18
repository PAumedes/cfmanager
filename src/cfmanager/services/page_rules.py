from typing import Any, Dict, List

from cfmanager.core.client import CloudflareClient
from cfmanager.core.decorators import cf_api
from cfmanager.core.logger import get_logger

logger = get_logger()


def _serialize_rule(r) -> Dict[str, Any]:
    target = ""
    if r.targets:
        t = r.targets[0]
        target = getattr(getattr(t, "constraint", None), "value", str(t))
    actions = [getattr(a, "id", str(a)) for a in (r.actions or [])]
    return {
        "id": r.id,
        "status": getattr(r, "status", ""),
        "target": target,
        "actions": ", ".join(actions),
    }


class PageRulesService:
    def __init__(self, client: CloudflareClient):
        self.client = client

    @cf_api("listing page rules")
    def list_page_rules(self, zone_id: str) -> List[Dict[str, Any]]:
        rules = self.client.sync_client.page_rules.list(zone_id=zone_id)
        return [_serialize_rule(r) for r in rules]

    @cf_api("getting page rule")
    def get_page_rule(self, zone_id: str, rule_id: str) -> Dict[str, Any]:
        r = self.client.sync_client.page_rules.get(pagerule_id=rule_id, zone_id=zone_id)
        return _serialize_rule(r)

    @cf_api("deleting page rule")
    def delete_page_rule(self, zone_id: str, rule_id: str) -> str:
        self.client.sync_client.page_rules.delete(pagerule_id=rule_id, zone_id=zone_id)
        return rule_id

    @cf_api("listing page rules async")
    async def list_page_rules_async(self, zone_id: str) -> List[Dict[str, Any]]:
        page = await self.client.async_client.page_rules.list(zone_id=zone_id)
        results = []
        async for r in page:
            results.append(_serialize_rule(r))
        return results

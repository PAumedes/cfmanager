from typing import Any, Dict, List

from cfmanager.core.client import CloudflareClient
from cfmanager.core.decorators import cf_api
from cfmanager.core.logger import get_logger

logger = get_logger()


class EmailRoutingService:
    def __init__(self, client: CloudflareClient):
        self.client = client

    @cf_api("getting email routing status")
    def get_status(self, zone_id: str) -> Dict[str, Any]:
        s = self.client.sync_client.email_routing.get(zone_id=zone_id)
        return {
            "enabled": getattr(s, "enabled", False),
            "name": getattr(s, "name", ""),
            "tag": getattr(s, "tag", ""),
            "modified_on": getattr(s, "modified_on", ""),
        }

    @cf_api("enabling email routing")
    def enable(self, zone_id: str) -> Dict[str, Any]:
        r = self.client.sync_client.email_routing.enable(zone_id=zone_id)
        return {"enabled": getattr(r, "enabled", True)}

    @cf_api("disabling email routing")
    def disable(self, zone_id: str) -> Dict[str, Any]:
        r = self.client.sync_client.email_routing.disable(zone_id=zone_id)
        return {"enabled": getattr(r, "enabled", False)}

    @cf_api("listing email routing rules")
    def list_rules(self, zone_id: str) -> List[Dict[str, Any]]:
        rules = self.client.sync_client.email_routing.rules.list(zone_id=zone_id)
        results = []
        for rule in rules:
            matchers = getattr(rule, "matchers", [])
            match_str = "; ".join(
                f"{getattr(m, 'field', '')}={getattr(m, 'value', '')}" for m in matchers
            )
            actions = getattr(rule, "actions", [])
            action_str = "; ".join(
                f"{getattr(a, 'type', '')}:{','.join(getattr(a, 'value', []) or [])}"
                for a in actions
            )
            results.append(
                {
                    "id": rule.id,
                    "name": getattr(rule, "name", ""),
                    "enabled": getattr(rule, "enabled", False),
                    "priority": getattr(rule, "priority", 0),
                    "matchers": match_str,
                    "actions": action_str,
                }
            )
        return results

    @cf_api("listing email destination addresses")
    def list_addresses(self) -> List[Dict[str, Any]]:
        account_id = self.client.get_account_id()
        addresses = self.client.sync_client.email_routing.addresses.list(account_id=account_id)
        return [
            {
                "id": a.id,
                "email": getattr(a, "email", ""),
                "verified": getattr(a, "verified", ""),
            }
            for a in addresses
        ]

from typing import Any, Dict, List

from cfmanager.core.client import CloudflareClient
from cfmanager.core.decorators import cf_api
from cfmanager.core.exceptions import ValidationError
from cfmanager.core.logger import get_logger

logger = get_logger()

_VALID_MODES = {"block", "challenge", "js_challenge", "managed_challenge", "whitelist", "allow"}


class FirewallService:
    def __init__(self, client: CloudflareClient):
        self.client = client

    @cf_api("listing IP access rules")
    def list_access_rules(self, zone_id: str) -> List[Dict[str, Any]]:
        rules = self.client.sync_client.firewall.access_rules.list(zone_id=zone_id)
        return [
            {
                "id": r.id,
                "mode": getattr(r, "mode", ""),
                "notes": getattr(r, "notes", ""),
                "target": getattr(r.configuration, "target", ""),
                "value": getattr(r.configuration, "value", ""),
            }
            for r in rules
        ]

    @cf_api("creating IP access rule")
    def create_access_rule(
        self, zone_id: str, mode: str, target: str, value: str, notes: str = ""
    ) -> Dict[str, Any]:
        if mode not in _VALID_MODES:
            raise ValidationError(
                f"Invalid mode '{mode}'. Must be one of: {', '.join(sorted(_VALID_MODES))}"
            )
        r = self.client.sync_client.firewall.access_rules.create(
            zone_id=zone_id,
            mode=mode,
            configuration={"target": target, "value": value},
        )
        return {
            "id": r.id,
            "mode": getattr(r, "mode", mode),
            "notes": getattr(r, "notes", notes),
            "target": getattr(r.configuration, "target", target),
            "value": getattr(r.configuration, "value", value),
        }

    @cf_api("deleting IP access rule")
    def delete_access_rule(self, zone_id: str, rule_id: str) -> str:
        self.client.sync_client.firewall.access_rules.delete(
            identifier=rule_id, zone_id=zone_id
        )
        return rule_id

    @cf_api("listing WAF packages")
    def list_waf_packages(self, zone_id: str) -> List[Dict[str, Any]]:
        packages = self.client.sync_client.firewall.waf.packages.list(zone_id=zone_id)
        return [
            {
                "id": p.id,
                "name": getattr(p, "name", ""),
                "description": getattr(p, "description", ""),
                "detection_mode": getattr(p, "detection_mode", ""),
            }
            for p in packages
        ]

    @cf_api("listing IP access rules async")
    async def list_access_rules_async(self, zone_id: str) -> List[Dict[str, Any]]:
        page = await self.client.async_client.firewall.access_rules.list(zone_id=zone_id)
        results = []
        async for r in page:
            results.append(
                {
                    "id": r.id,
                    "mode": getattr(r, "mode", ""),
                    "notes": getattr(r, "notes", ""),
                    "target": getattr(r.configuration, "target", ""),
                    "value": getattr(r.configuration, "value", ""),
                }
            )
        return results

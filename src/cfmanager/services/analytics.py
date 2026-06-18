from typing import Any, Dict

from cfmanager.core.client import CloudflareClient
from cfmanager.core.decorators import cf_api
from cfmanager.core.logger import get_logger

logger = get_logger()


class AnalyticsService:
    def __init__(self, client: CloudflareClient):
        self.client = client

    @cf_api("fetching R2 usage summary")
    def r2_usage_summary(self) -> Dict[str, Any]:
        account_id = self.client.get_account_id()
        result = self.client.sync_client.r2.buckets.list(account_id=account_id)
        raw_buckets = getattr(result, "buckets", result) or []
        buckets = [
            {
                "name": getattr(b, "name", ""),
                "location": getattr(b, "location", ""),
                "created": getattr(b, "creation_date", ""),
            }
            for b in raw_buckets
        ]
        return {
            "bucket_count": len(buckets),
            "buckets": buckets,
        }

    @cf_api("fetching zone summary")
    def zone_summary(self) -> Dict[str, Any]:
        zones_raw = list(self.client.sync_client.zones.list())
        zones = [
            {
                "id": z.id,
                "name": z.name,
                "status": z.status,
                "paused": z.paused,
            }
            for z in zones_raw
        ]
        return {
            "total_zones": len(zones),
            "active": sum(1 for z in zones if z["status"] == "active"),
            "paused": sum(1 for z in zones if z["paused"]),
            "zones": zones,
        }

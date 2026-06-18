from typing import Any, Dict

from cfmanager.core.client import CloudflareClient
from cfmanager.core.exceptions import APIError
from cfmanager.core.logger import get_logger
from cfmanager.services.dns import DNSService
from cfmanager.services.ssl import SSLService
from cfmanager.services.zones import ZoneService

logger = get_logger()


class BackupService:
    def __init__(self, client: CloudflareClient):
        self.client = client
        self._zones = ZoneService(client)
        self._dns = DNSService(client)
        self._ssl = SSLService(client)

    def backup_zone(self, zone_id: str) -> Dict[str, Any]:
        try:
            logger.info(f"Backing up zone {zone_id}")
            zone = self._zones.get_zone(zone_id)
            dns_records = self._dns.list_dns_records(zone_id)
            ssl_setting = self._ssl.get_ssl_setting(zone_id)
            return {
                "version": 1,
                "zone_id": zone_id,
                "zone_name": zone["name"],
                "dns_records": dns_records,
                "ssl": {"mode": ssl_setting["mode"]},
            }
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to back up zone {zone_id}")
            raise APIError(f"Backup error for zone {zone_id}: {str(e)}") from e

    def restore_zone(self, zone_id: str, data: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        results: Dict[str, Any] = {"dns_created": 0, "ssl_set": False}
        try:
            logger.info(f"Restoring zone {zone_id} (dry_run={dry_run})")
            for record in data.get("dns_records", []):
                if not dry_run:
                    self._dns.create_dns_record(
                        zone_id=zone_id,
                        name=record["name"],
                        type=record["type"],
                        content=record["content"],
                        ttl=record.get("ttl", 3600),
                        proxied=record.get("proxied", False),
                    )
                results["dns_created"] += 1

            ssl_data = data.get("ssl", {})
            if ssl_data.get("mode"):
                if not dry_run:
                    self._ssl.set_ssl_mode(zone_id, ssl_data["mode"])
                results["ssl_set"] = True

            return results
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Failed to restore zone {zone_id}")
            raise APIError(f"Restore error for zone {zone_id}: {str(e)}") from e

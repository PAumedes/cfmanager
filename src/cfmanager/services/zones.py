from typing import List, Dict, Any, Optional

from cfmanager.core.client import CloudflareClient
from cfmanager.core.exceptions import APIError, ValidationError
from cfmanager.core.logger import get_logger

logger = get_logger()

class ZoneService:
    def __init__(self, client: CloudflareClient):
        self.client = client

    # --- Sync Methods (for CLI) ---

    def list_zones(self, name: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Listing zones (filter name={name})")
            params = {}
            if name:
                params["name"] = name
            
            zones = self.client.sync_client.zones.list(**params)
            results = []
            for zone in zones:
                results.append({
                    "id": zone.id,
                    "name": zone.name,
                    "status": zone.status,
                    "paused": zone.paused,
                    "type": zone.type,
                    "development_mode": getattr(zone, 'development_mode', 0)
                })
            return results
        except Exception as e:
            logger.exception("Failed to list zones")
            raise APIError(f"Cloudflare API error listing zones: {str(e)}") from e

    def get_zone(self, zone_id: str) -> Dict[str, Any]:
        try:
            logger.debug(f"Getting zone details for {zone_id}")
            zone = self.client.sync_client.zones.get(zone_id=zone_id)
            return {
                "id": zone.id,
                "name": zone.name,
                "status": zone.status,
                "paused": zone.paused,
                "type": zone.type,
                "development_mode": getattr(zone, 'development_mode', 0),
                "name_servers": getattr(zone, 'name_servers', []),
                "original_name_servers": getattr(zone, 'original_name_servers', [])
            }
        except Exception as e:
            logger.exception(f"Failed to get zone {zone_id}")
            raise APIError(f"Cloudflare API error getting zone: {str(e)}") from e

    def delete_zone(self, zone_id: str) -> str:
        try:
            logger.warning(f"Deleting zone {zone_id}")
            self.client.sync_client.zones.delete(zone_id=zone_id)
            return zone_id
        except Exception as e:
            logger.exception(f"Failed to delete zone {zone_id}")
            raise APIError(f"Cloudflare API error deleting zone: {str(e)}") from e

    def purge_cache(
        self,
        zone_id: str,
        files: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        hosts: Optional[List[str]] = None,
        prefixes: Optional[List[str]] = None,
        purge_everything: bool = False,
    ) -> bool:
        if not any([files, tags, hosts, prefixes, purge_everything]):
            raise ValidationError("purge_cache requires at least one of: purge_everything, files, tags, hosts, prefixes.")
        if purge_everything and any([files, tags, hosts, prefixes]):
            raise ValidationError("purge_everything cannot be combined with files, tags, hosts, or prefixes.")
        try:
            logger.info(f"Purging cache for zone {zone_id}")
            params: Dict[str, Any] = {"zone_id": zone_id}
            if purge_everything:
                params["purge_everything"] = True
            else:
                if files:
                    params["files"] = files
                if tags:
                    params["tags"] = tags
                if hosts:
                    params["hosts"] = hosts
                if prefixes:
                    params["prefixes"] = prefixes
            self.client.sync_client.zones.purge_cache(**params)
            return True
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to purge cache for {zone_id}")
            raise APIError(f"Cloudflare API error purging cache: {str(e)}") from e

    # --- Async Methods (for TUI) ---

    async def list_zones_async(self, name: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Listing zones asynchronously (filter name={name})")
            params = {}
            if name:
                params["name"] = name
            
            zones_page = await self.client.async_client.zones.list(**params)
            results = []
            async for zone in zones_page:
                results.append({
                    "id": zone.id,
                    "name": zone.name,
                    "status": zone.status,
                    "paused": zone.paused,
                    "type": zone.type,
                    "development_mode": getattr(zone, 'development_mode', 0)
                })
            return results
        except Exception as e:
            logger.exception("Failed to list zones asynchronously")
            raise APIError(f"Cloudflare API error listing zones: {str(e)}") from e

    async def get_zone_async(self, zone_id: str) -> Dict[str, Any]:
        try:
            logger.debug(f"Getting zone details asynchronously for {zone_id}")
            zone = await self.client.async_client.zones.get(zone_id=zone_id)
            return {
                "id": zone.id,
                "name": zone.name,
                "status": zone.status,
                "paused": zone.paused,
                "type": zone.type,
                "development_mode": getattr(zone, 'development_mode', 0),
                "name_servers": getattr(zone, 'name_servers', []),
                "original_name_servers": getattr(zone, 'original_name_servers', [])
            }
        except Exception as e:
            logger.exception(f"Failed to get zone asynchronously {zone_id}")
            raise APIError(f"Cloudflare API error getting zone: {str(e)}") from e

    async def delete_zone_async(self, zone_id: str) -> str:
        try:
            logger.warning(f"Deleting zone asynchronously {zone_id}")
            await self.client.async_client.zones.delete(zone_id=zone_id)
            return zone_id
        except Exception as e:
            logger.exception(f"Failed to delete zone asynchronously {zone_id}")
            raise APIError(f"Cloudflare API error deleting zone: {str(e)}") from e

    async def purge_cache_async(
        self,
        zone_id: str,
        files: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        hosts: Optional[List[str]] = None,
        prefixes: Optional[List[str]] = None,
        purge_everything: bool = False,
    ) -> bool:
        if not any([files, tags, hosts, prefixes, purge_everything]):
            raise ValidationError("purge_cache requires at least one of: purge_everything, files, tags, hosts, prefixes.")
        if purge_everything and any([files, tags, hosts, prefixes]):
            raise ValidationError("purge_everything cannot be combined with files, tags, hosts, or prefixes.")
        try:
            logger.info(f"Purging cache asynchronously for zone {zone_id}")
            params: Dict[str, Any] = {"zone_id": zone_id}
            if purge_everything:
                params["purge_everything"] = True
            else:
                if files:
                    params["files"] = files
                if tags:
                    params["tags"] = tags
                if hosts:
                    params["hosts"] = hosts
                if prefixes:
                    params["prefixes"] = prefixes
            await self.client.async_client.zones.purge_cache(**params)
            return True
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to purge cache asynchronously for {zone_id}")
            raise APIError(f"Cloudflare API error purging cache: {str(e)}") from e

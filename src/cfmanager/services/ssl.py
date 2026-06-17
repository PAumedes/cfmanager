from typing import List, Dict, Any

from cfmanager.core.client import CloudflareClient
from cfmanager.core.exceptions import APIError, ValidationError
from cfmanager.core.logger import get_logger

logger = get_logger()

VALID_SSL_MODES = {"off", "flexible", "full", "strict"}


class SSLService:
    def __init__(self, client: CloudflareClient):
        self.client = client

    def _validate_ssl_mode(self, mode: str):
        if mode not in VALID_SSL_MODES:
            raise ValidationError(
                f"Invalid SSL mode '{mode}'. Must be one of: {', '.join(sorted(VALID_SSL_MODES))}"
            )

    # --- Sync Methods (for CLI) ---

    def get_ssl_setting(self, zone_id: str) -> Dict[str, Any]:
        try:
            logger.debug(f"Getting SSL setting for zone {zone_id}")
            ssl_setting = self.client.sync_client.zones.settings.get("ssl", zone_id=zone_id)
            mode = getattr(ssl_setting, 'value', None)

            cert_packs_page = self.client.sync_client.ssl.certificate_packs.list(zone_id=zone_id)
            certificate_packs = []
            for pack in cert_packs_page:
                certificate_packs.append({
                    "id": getattr(pack, 'id', None),
                    "type": getattr(pack, 'type', None),
                    "status": getattr(pack, 'status', None),
                    "hosts": getattr(pack, 'hosts', []),
                })

            return {
                "zone_id": zone_id,
                "mode": mode,
                "enabled_protocols": getattr(ssl_setting, 'enabled_protocols', []),
                "certificate_packs": certificate_packs,
            }
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to get SSL setting for zone {zone_id}")
            raise APIError(f"Cloudflare API error getting SSL setting: {str(e)}") from e

    def set_ssl_mode(self, zone_id: str, mode: str) -> Dict[str, Any]:
        self._validate_ssl_mode(mode)
        try:
            logger.info(f"Setting SSL mode for zone {zone_id} to '{mode}'")
            result = self.client.sync_client.zones.settings.edit(
                "ssl", zone_id=zone_id, value=mode
            )
            return {
                "zone_id": zone_id,
                "mode": getattr(result, 'value', mode),
            }
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to set SSL mode for zone {zone_id}")
            raise APIError(f"Cloudflare API error setting SSL mode: {str(e)}") from e

    def list_cert_packs(self, zone_id: str) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Listing certificate packs for zone {zone_id}")
            cert_packs_page = self.client.sync_client.ssl.certificate_packs.list(zone_id=zone_id)
            results = []
            for pack in cert_packs_page:
                results.append({
                    "id": getattr(pack, 'id', None),
                    "type": getattr(pack, 'type', None),
                    "status": getattr(pack, 'status', None),
                    "hosts": getattr(pack, 'hosts', []),
                    "primary_certificate": getattr(pack, 'primary_certificate', None),
                })
            return results
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to list certificate packs for zone {zone_id}")
            raise APIError(f"Cloudflare API error listing certificate packs: {str(e)}") from e

    # --- Async Methods (for TUI) ---

    async def get_ssl_setting_async(self, zone_id: str) -> Dict[str, Any]:
        try:
            logger.debug(f"Getting SSL setting asynchronously for zone {zone_id}")
            ssl_setting = await self.client.async_client.zones.settings.get("ssl", zone_id=zone_id)
            mode = getattr(ssl_setting, 'value', None)

            cert_packs_page = await self.client.async_client.ssl.certificate_packs.list(zone_id=zone_id)
            certificate_packs = []
            async for pack in cert_packs_page:
                certificate_packs.append({
                    "id": getattr(pack, 'id', None),
                    "type": getattr(pack, 'type', None),
                    "status": getattr(pack, 'status', None),
                    "hosts": getattr(pack, 'hosts', []),
                })

            return {
                "zone_id": zone_id,
                "mode": mode,
                "enabled_protocols": getattr(ssl_setting, 'enabled_protocols', []),
                "certificate_packs": certificate_packs,
            }
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to get SSL setting asynchronously for zone {zone_id}")
            raise APIError(f"Cloudflare API error getting SSL setting: {str(e)}") from e

    async def set_ssl_mode_async(self, zone_id: str, mode: str) -> Dict[str, Any]:
        self._validate_ssl_mode(mode)
        try:
            logger.info(f"Setting SSL mode asynchronously for zone {zone_id} to '{mode}'")
            result = await self.client.async_client.zones.settings.edit(
                "ssl", zone_id=zone_id, value=mode
            )
            return {
                "zone_id": zone_id,
                "mode": getattr(result, 'value', mode),
            }
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to set SSL mode asynchronously for zone {zone_id}")
            raise APIError(f"Cloudflare API error setting SSL mode: {str(e)}") from e

    async def list_cert_packs_async(self, zone_id: str) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Listing certificate packs asynchronously for zone {zone_id}")
            cert_packs_page = await self.client.async_client.ssl.certificate_packs.list(zone_id=zone_id)
            results = []
            async for pack in cert_packs_page:
                results.append({
                    "id": getattr(pack, 'id', None),
                    "type": getattr(pack, 'type', None),
                    "status": getattr(pack, 'status', None),
                    "hosts": getattr(pack, 'hosts', []),
                    "primary_certificate": getattr(pack, 'primary_certificate', None),
                })
            return results
        except (APIError, ValidationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to list certificate packs asynchronously for zone {zone_id}")
            raise APIError(f"Cloudflare API error listing certificate packs: {str(e)}") from e

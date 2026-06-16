from typing import List, Dict, Any, Optional
from cfmanager.core.client import CloudflareClient
from cfmanager.core.exceptions import APIError, ValidationError
from cfmanager.core.logger import get_logger

logger = get_logger()

class DNSService:
    def __init__(self, client: CloudflareClient):
        self.client = client

    def _validate_record(self, name: str, type: str, content: str):
        if not name:
            raise ValidationError("DNS record name cannot be empty.")
        if not type:
            raise ValidationError("DNS record type cannot be empty.")
        if not content:
            raise ValidationError("DNS record content cannot be empty.")
        
        valid_types = {"A", "AAAA", "CNAME", "TXT", "MX", "NS", "SRV", "CAA", "LOC"}
        if type.upper() not in valid_types:
            raise ValidationError(f"Invalid DNS record type '{type}'. Must be one of: {', '.join(valid_types)}")

    # --- Sync Methods (for CLI) ---

    def list_dns_records(
        self, zone_id: str, name: Optional[str] = None, type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Listing DNS records for zone {zone_id} (filter name={name}, type={type})")
            params = {}
            if name:
                params["name"] = name
            if type:
                params["type"] = type.upper()

            records = self.client.sync_client.dns.records.list(zone_id=zone_id, **params)
            results = []
            for record in records:
                results.append({
                    "id": record.id,
                    "name": record.name,
                    "type": record.type,
                    "content": record.content,
                    "ttl": record.ttl,
                    "proxied": getattr(record, 'proxied', False),
                    "comment": getattr(record, 'comment', "")
                })
            return results
        except Exception as e:
            logger.exception(f"Failed to list DNS records for {zone_id}")
            raise APIError(f"Cloudflare API error listing DNS records: {str(e)}") from e

    def create_dns_record(
        self, zone_id: str, name: str, type: str, content: str, ttl: int = 3600, proxied: bool = False
    ) -> Dict[str, Any]:
        self._validate_record(name, type, content)
        try:
            logger.info(f"Creating {type} record for zone {zone_id}: {name} -> {content}")
            record = self.client.sync_client.dns.records.create(
                zone_id=zone_id,
                name=name,
                type=type.upper(),
                content=content,
                ttl=ttl,
                proxied=proxied
            )
            return {
                "id": record.id,
                "name": record.name,
                "type": record.type,
                "content": record.content,
                "ttl": record.ttl,
                "proxied": getattr(record, 'proxied', False)
            }
        except Exception as e:
            logger.exception(f"Failed to create DNS record for {zone_id}")
            raise APIError(f"Cloudflare API error creating DNS record: {str(e)}") from e

    def edit_dns_record(
        self,
        zone_id: str,
        record_id: str,
        name: Optional[str] = None,
        type: Optional[str] = None,
        content: Optional[str] = None,
        ttl: Optional[int] = None,
        proxied: Optional[bool] = None
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Editing DNS record {record_id} in zone {zone_id}")
            params = {}
            if name is not None:
                params["name"] = name
            if type is not None:
                params["type"] = type.upper()
            if content is not None:
                params["content"] = content
            if ttl is not None:
                params["ttl"] = ttl
            if proxied is not None:
                params["proxied"] = proxied

            record = self.client.sync_client.dns.records.edit(
                dns_record_id=record_id,
                zone_id=zone_id,
                **params
            )
            return {
                "id": record.id,
                "name": record.name,
                "type": record.type,
                "content": record.content,
                "ttl": record.ttl,
                "proxied": getattr(record, 'proxied', False)
            }
        except Exception as e:
            logger.exception(f"Failed to edit DNS record {record_id}")
            raise APIError(f"Cloudflare API error editing DNS record: {str(e)}") from e

    def delete_dns_record(self, zone_id: str, record_id: str) -> str:
        try:
            logger.warning(f"Deleting DNS record {record_id} in zone {zone_id}")
            self.client.sync_client.dns.records.delete(
                dns_record_id=record_id,
                zone_id=zone_id
            )
            return record_id
        except Exception as e:
            logger.exception(f"Failed to delete DNS record {record_id}")
            raise APIError(f"Cloudflare API error deleting DNS record: {str(e)}") from e

    # --- Async Methods (for TUI) ---

    async def list_dns_records_async(
        self, zone_id: str, name: Optional[str] = None, type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Listing DNS records asynchronously for zone {zone_id} (filter name={name}, type={type})")
            params = {}
            if name:
                params["name"] = name
            if type:
                params["type"] = type.upper()

            records_page = await self.client.async_client.dns.records.list(zone_id=zone_id, **params)
            results = []
            async for record in records_page:
                results.append({
                    "id": record.id,
                    "name": record.name,
                    "type": record.type,
                    "content": record.content,
                    "ttl": record.ttl,
                    "proxied": getattr(record, 'proxied', False),
                    "comment": getattr(record, 'comment', "")
                })
            return results
        except Exception as e:
            logger.exception(f"Failed to list DNS records asynchronously for {zone_id}")
            raise APIError(f"Cloudflare API error listing DNS records: {str(e)}") from e

    async def create_dns_record_async(
        self, zone_id: str, name: str, type: str, content: str, ttl: int = 3600, proxied: bool = False
    ) -> Dict[str, Any]:
        self._validate_record(name, type, content)
        try:
            logger.info(f"Creating {type} record asynchronously for zone {zone_id}: {name} -> {content}")
            record = await self.client.async_client.dns.records.create(
                zone_id=zone_id,
                name=name,
                type=type.upper(),
                content=content,
                ttl=ttl,
                proxied=proxied
            )
            return {
                "id": record.id,
                "name": record.name,
                "type": record.type,
                "content": record.content,
                "ttl": record.ttl,
                "proxied": getattr(record, 'proxied', False)
            }
        except Exception as e:
            logger.exception(f"Failed to create DNS record asynchronously for {zone_id}")
            raise APIError(f"Cloudflare API error creating DNS record: {str(e)}") from e

    async def edit_dns_record_async(
        self,
        zone_id: str,
        record_id: str,
        name: Optional[str] = None,
        type: Optional[str] = None,
        content: Optional[str] = None,
        ttl: Optional[int] = None,
        proxied: Optional[bool] = None
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Editing DNS record asynchronously {record_id} in zone {zone_id}")
            params = {}
            if name is not None:
                params["name"] = name
            if type is not None:
                params["type"] = type.upper()
            if content is not None:
                params["content"] = content
            if ttl is not None:
                params["ttl"] = ttl
            if proxied is not None:
                params["proxied"] = proxied

            record = await self.client.async_client.dns.records.edit(
                dns_record_id=record_id,
                zone_id=zone_id,
                **params
            )
            return {
                "id": record.id,
                "name": record.name,
                "type": record.type,
                "content": record.content,
                "ttl": record.ttl,
                "proxied": getattr(record, 'proxied', False)
            }
        except Exception as e:
            logger.exception(f"Failed to edit DNS record asynchronously {record_id}")
            raise APIError(f"Cloudflare API error editing DNS record: {str(e)}") from e

    async def delete_dns_record_async(self, zone_id: str, record_id: str) -> str:
        try:
            logger.warning(f"Deleting DNS record asynchronously {record_id} in zone {zone_id}")
            await self.client.async_client.dns.records.delete(
                dns_record_id=record_id,
                zone_id=zone_id
            )
            return record_id
        except Exception as e:
            logger.exception(f"Failed to delete DNS record asynchronously {record_id}")
            raise APIError(f"Cloudflare API error deleting DNS record: {str(e)}") from e

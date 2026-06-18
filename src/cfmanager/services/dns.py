import csv
import io
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
        if proxied:
            ttl = 1  # Cloudflare requires TTL=1 (Auto) when proxied
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
            if proxied:
                ttl = 1  # Cloudflare requires TTL=1 (Auto) when proxied
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
        if proxied:
            ttl = 1  # Cloudflare requires TTL=1 (Auto) when proxied
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
            if proxied:
                ttl = 1  # Cloudflare requires TTL=1 (Auto) when proxied
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

    # --- Cross-zone search ---

    def find_records_across_zones(
        self, zones: List[Dict[str, Any]], name: str, type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = []
        for zone in zones:
            try:
                for record in self.list_dns_records(zone["id"], name=name, type=type):
                    results.append({**record, "zone_id": zone["id"], "zone_name": zone["name"]})
            except APIError as e:
                logger.warning(f"Skipping zone {zone.get('name', zone['id'])}: {e}")
        return results

    # --- Import / Export ---

    _EXPORT_FORMATS = {"csv", "bind"}
    _CSV_FIELDS = ["name", "type", "content", "ttl", "proxied", "comment"]

    def export_records(self, zone_id: str, format: str = "csv") -> str:
        if format not in self._EXPORT_FORMATS:
            raise ValidationError(f"Unknown export format '{format}'. Must be one of: {', '.join(sorted(self._EXPORT_FORMATS))}")
        records = self.list_dns_records(zone_id)
        if format == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=self._CSV_FIELDS, extrasaction="ignore", lineterminator="\n")
            writer.writeheader()
            for r in records:
                writer.writerow({f: r.get(f, "") for f in self._CSV_FIELDS})
            return output.getvalue()
        # bind
        lines = ["; Generated by cfmanager"]
        for r in records:
            lines.append(f'{r["name"]} {r["ttl"]} IN {r["type"]} {r["content"]}')
        return "\n".join(lines) + "\n"

    def import_records(
        self, zone_id: str, content: str, format: str = "csv", dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        if format not in self._EXPORT_FORMATS:
            raise ValidationError(f"Unknown import format '{format}'. Must be one of: {', '.join(sorted(self._EXPORT_FORMATS))}")

        parsed: List[Dict[str, Any]] = []
        if format == "csv":
            reader = csv.DictReader(io.StringIO(content))
            required = {"name", "type", "content"}
            missing = required - set(reader.fieldnames or [])
            if missing:
                raise ValidationError(f"CSV is missing required column(s): {', '.join(sorted(missing))}")
            for row in reader:
                parsed.append({
                    "name": row["name"],
                    "type": row["type"].upper(),
                    "content": row["content"],
                    "ttl": int(row.get("ttl") or 3600),
                    "proxied": (row.get("proxied") or "false").lower() == "true",
                    "comment": row.get("comment", ""),
                })
        else:  # bind
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith(";") or line.startswith("$"):
                    continue
                parts = line.split()
                if len(parts) < 4:
                    continue
                # Formats: "name IN type content..." or "name ttl IN type content..."
                if parts[1].upper() == "IN":
                    name, type_, rest = parts[0], parts[2], parts[3:]
                    ttl = 3600
                else:
                    if len(parts) < 5:
                        continue  # ttl-present line with no content — skip
                    name, ttl, type_, rest = parts[0], int(parts[1]), parts[3], parts[4:]
                parsed.append({
                    "name": name,
                    "type": type_.upper(),
                    "content": " ".join(rest),
                    "ttl": ttl,
                    "proxied": False,
                    "comment": "",
                })

        if dry_run:
            return parsed

        results = []
        for i, r in enumerate(parsed):
            try:
                created = self.create_dns_record(
                    zone_id=zone_id,
                    name=r["name"],
                    type=r["type"],
                    content=r["content"],
                    ttl=r["ttl"],
                    proxied=r["proxied"],
                )
            except APIError as e:
                raise APIError(
                    f"Import failed on record {i + 1}/{len(parsed)} ('{r['name']}'): {e}. "
                    f"{i} record(s) were already created."
                ) from e
            results.append(created)
        return results

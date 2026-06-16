from typing import Optional
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, DataTable
from textual.containers import Container
from cfmanager.services.dns import DNSService
from cfmanager.tui.widgets.dialogs import ConfirmDialog, DNSFormDialog
from cfmanager.core.logger import get_logger

logger = get_logger()

class DNSView(Widget):
    def __init__(self, **kwargs) -> None:
        self.zone_id: Optional[str] = None
        self.zone_name: Optional[str] = None
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Container(id="main-content"):
            self.title_label = Label("🔑 DNS Records", id="screen-title")
            yield self.title_label
            yield Label("Press [bold]a[/bold] to add, [bold]e[/bold] to edit, [bold]d[/bold] to delete, [bold]r[/bold] to refresh.")
            yield DataTable(id="dns-table")

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("ID", "Name", "Type", "Content", "TTL", "Proxied")
        
    def set_zone(self, zone_id: str, zone_name: str) -> None:
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.title_label.update(f"🔑 DNS Records for {self.zone_name}")
        self.run_worker(self.refresh_records())

    async def refresh_records(self) -> None:
        if not self.zone_id:
            self.title_label.update("🔑 DNS Records (No Zone Selected)")
            return
            
        table = self.query_one(DataTable)
        table.clear()
        
        dns_service = DNSService(self.app.cf_client)
        try:
            records = await dns_service.list_dns_records_async(self.zone_id)
            for record in records:
                table.add_row(
                    record["id"],
                    record["name"],
                    record["type"],
                    record["content"],
                    str(record["ttl"]),
                    "Yes" if record["proxied"] else "No",
                    key=record["id"]
                )
        except Exception as e:
            logger.exception("Failed to load DNS records in TUI")
            self.app.notify(f"Error loading DNS records: {e}", severity="error")

    async def on_key(self, event) -> None:
        if not self.zone_id:
            return

        table = self.query_one(DataTable)
        
        if event.key == "r":
            await self.refresh_records()
            return
            
        if event.key == "a":
            async def on_dns_add(data) -> None:
                if data:
                    dns_service = DNSService(self.app.cf_client)
                    try:
                        await dns_service.create_dns_record_async(
                            zone_id=self.zone_id,
                            name=data["name"],
                            type=data["type"],
                            content=data["content"],
                            ttl=data["ttl"],
                            proxied=data["proxied"]
                        )
                        self.app.notify("Successfully added DNS record", severity="success")
                        await self.refresh_records()
                    except Exception as e:
                        self.app.notify(f"Add failed: {e}", severity="error")

            self.app.push_screen(DNSFormDialog(), on_dns_add)
            return

        if table.cursor_row is None or table.row_count == 0:
            return

        row_key = table.row_keys[table.cursor_row]
        row_values = table.get_row(row_key)
        
        record_id = row_values[0]
        record_name = row_values[1]
        record_type = row_values[2]
        record_content = row_values[3]
        record_ttl = int(row_values[4])
        record_proxied = row_values[5] == "Yes"

        if event.key == "d":
            async def confirm_delete(confirm: bool) -> None:
                if confirm:
                    dns_service = DNSService(self.app.cf_client)
                    try:
                        await dns_service.delete_dns_record_async(self.zone_id, record_id)
                        self.app.notify("Deleted DNS record", severity="success")
                        await self.refresh_records()
                    except Exception as e:
                        self.app.notify(f"Delete failed: {e}", severity="error")

            self.app.push_screen(
                ConfirmDialog(f"Are you sure you want to delete record {record_name} ({record_type})?"),
                confirm_delete
            )
            
        elif event.key == "e":
            current_record = {
                "id": record_id,
                "name": record_name,
                "type": record_type,
                "content": record_content,
                "ttl": record_ttl,
                "proxied": record_proxied
            }
            
            async def on_dns_edit(data) -> None:
                if data:
                    dns_service = DNSService(self.app.cf_client)
                    try:
                        await dns_service.edit_dns_record_async(
                            zone_id=self.zone_id,
                            record_id=record_id,
                            name=data["name"],
                            type=data["type"],
                            content=data["content"],
                            ttl=data["ttl"],
                            proxied=data["proxied"]
                        )
                        self.app.notify("Successfully updated DNS record", severity="success")
                        await self.refresh_records()
                    except Exception as e:
                        self.app.notify(f"Update failed: {e}", severity="error")

            self.app.push_screen(DNSFormDialog(current_record), on_dns_edit)

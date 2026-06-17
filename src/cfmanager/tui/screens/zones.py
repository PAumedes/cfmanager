import time

from textual.app import ComposeResult
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import DataTable, Label

from cfmanager.core.errors import format_error
from cfmanager.core.logger import get_logger
from cfmanager.services.zones import ZoneService
from cfmanager.tui.widgets.dialogs import ConfirmDialog
logger = get_logger()


class ZonesView(Widget):
    def __init__(self, **kwargs) -> None:
        self._last_loaded: float = 0.0
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Container(id="main-content"):
            yield Label("🌐 Zones / Domains", id="screen-title")
            yield Label("Press [bold]Enter[/bold] to manage DNS, [bold]d[/bold] to delete zone, [bold]p[/bold] to purge cache.")
            yield DataTable(id="zones-table")

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("ID", "Name", "Status", "Paused", "Type")
        self.run_worker(self.refresh_zones(), exclusive=True)

    async def refresh_zones(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        table.focus()
        
        zone_service = ZoneService(self.app.cf_client)
        try:
            zones = await zone_service.list_zones_async()
            for zone in zones:
                table.add_row(
                    zone["id"],
                    zone["name"],
                    zone["status"],
                    "Yes" if zone["paused"] else "No",
                    zone["type"],
                    key=zone["id"]
                )
            self._last_loaded = time.monotonic()
        except Exception as e:
            logger.exception("Failed to load zones in TUI")
            self.app.notify(f"Could not load zones: {format_error(e)}", severity="error")

    async def on_key(self, event) -> None:
        table = self.query_one(DataTable)
        
        if table.cursor_row is None or table.row_count == 0:
            return

        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        row_values = table.get_row(row_key)
        row_id = row_values[0]
        row_name = row_values[1]

        if event.key == "d":
            async def confirm_delete(confirm: bool) -> None:
                if confirm:
                    zone_service = ZoneService(self.app.cf_client)
                    try:
                        await zone_service.delete_zone_async(row_id)
                        self.app.notify(f"Deleted zone: {row_name}", severity="success")
                        await self.refresh_zones()
                    except Exception as e:
                        self.app.notify(f"Delete failed: {format_error(e)}", severity="error")

            self.app.push_screen(
                ConfirmDialog(f"Are you sure you want to delete zone '{row_name}'?"),
                confirm_delete
            )
        elif event.key == "p":
            async def confirm_purge(confirm: bool) -> None:
                if confirm:
                    zone_service = ZoneService(self.app.cf_client)
                    try:
                        await zone_service.purge_cache_async(row_id)
                        self.app.notify(f"Purged cache for {row_name}", severity="success")
                    except Exception as e:
                        self.app.notify(f"Purge failed: {format_error(e)}", severity="error")

            self.app.push_screen(
                ConfirmDialog(f"Purge all cache for zone '{row_name}'?"),
                confirm_purge
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        zone_id = event.row_key.value
        row_values = self.query_one(DataTable).get_row(event.row_key)
        zone_name = row_values[1]
        
        # Switch to DNS view and set active zone
        switcher = self.app.query_one("#content-switcher")
        dns_view = self.app.query_one("#dns")
        dns_view.set_zone(zone_id, zone_name)
        switcher.current = "dns"

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, DataTable, Label, Select

from cfmanager.core.logger import get_logger
from cfmanager.services.ssl import SSLService
from cfmanager.services.zones import ZoneService
logger = get_logger()

SSL_MODES = [
    ("off", "Off"),
    ("flexible", "Flexible"),
    ("full", "Full"),
    ("strict", "Full (Strict)"),
]


class SSLModeDialog(ModalScreen[Optional[str]]):
    def __init__(self, zone_name: str, current_mode: str) -> None:
        self.zone_name = zone_name
        self.current_mode = current_mode
        super().__init__()

    def compose(self) -> ComposeResult:
        with Grid(classes="dialog-container"):
            with Vertical(classes="dialog-box"):
                yield Label(f"Change SSL Mode — {self.zone_name}", classes="dialog-title")
                yield Label("Select SSL Mode")
                yield Select(
                    SSL_MODES,
                    value=self.current_mode,
                    id="ssl-mode-select",
                )
                with Horizontal():
                    yield Button("Save", variant="primary", id="ssl-save")
                    yield Button("Cancel", id="ssl-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ssl-save":
            mode = self.query_one("#ssl-mode-select").value
            self.dismiss(mode)
        else:
            self.dismiss(None)


class SSLView(Widget):
    def compose(self) -> ComposeResult:
        with Container(id="main-content"):
            yield Label("🔑 SSL/TLS Settings", id="screen-title")
            yield Label(
                "Press [bold]Enter[/bold] to view cert packs, "
                "[bold]s[/bold] to change SSL mode, [bold]r[/bold] to refresh."
            )
            yield DataTable(id="ssl-table")

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Zone Name", "SSL Mode", "Cert Count")
        self.run_worker(self.refresh_data())

    async def refresh_data(self) -> None:
        table = self.query_one(DataTable)
        table.clear()

        zone_service = ZoneService(self.app.cf_client)
        ssl_service = SSLService(self.app.cf_client)
        try:
            zones = await zone_service.list_zones_async()
            for zone in zones:
                zone_id = zone["id"]
                zone_name = zone["name"]
                try:
                    ssl_info = await ssl_service.get_ssl_setting_async(zone_id)
                    mode = ssl_info.get("mode", "unknown")
                    cert_packs = ssl_info.get("certificate_packs", [])
                    cert_count = str(len(cert_packs))
                except Exception:
                    mode = "error"
                    cert_count = "?"
                table.add_row(zone_name, mode, cert_count, key=zone_id)
        except Exception as e:
            logger.exception("Failed to load SSL data in TUI")
            self.app.notify(f"Error loading SSL data: {e}", severity="error")

    async def on_key(self, event) -> None:
        table = self.query_one(DataTable)

        if event.key == "r":
            await self.refresh_data()
            return

        if table.cursor_row is None or table.row_count == 0:
            return

        row_key = table.row_keys[table.cursor_row]
        zone_id = row_key.value
        row_values = table.get_row(row_key)
        zone_name = row_values[0]
        current_mode = row_values[1]

        if event.key == "s":
            async def on_mode_selected(mode: Optional[str]) -> None:
                if mode:
                    ssl_service = SSLService(self.app.cf_client)
                    try:
                        await ssl_service.set_ssl_mode_async(zone_id, mode)
                        self.app.notify(
                            f"SSL mode for {zone_name} set to '{mode}'",
                            severity="success",
                        )
                        await self.refresh_data()
                    except Exception as e:
                        self.app.notify(f"Failed to set SSL mode: {e}", severity="error")

            self.app.push_screen(
                SSLModeDialog(zone_name, current_mode),
                on_mode_selected,
            )

        elif event.key == "enter":
            ssl_service = SSLService(self.app.cf_client)
            try:
                packs = await ssl_service.list_cert_packs_async(zone_id)
                if not packs:
                    self.app.notify(f"No certificate packs for {zone_name}.", severity="information")
                else:
                    lines = [f"{p.get('type', '?')} | {p.get('status', '?')} | hosts: {', '.join(p.get('hosts', []))}" for p in packs]
                    self.app.notify(
                        f"Cert packs for {zone_name}:\n" + "\n".join(lines),
                        severity="information",
                        timeout=10,
                    )
            except Exception as e:
                self.app.notify(f"Error loading cert packs: {e}", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Row selection (Enter) is also handled here for drill-down
        pass

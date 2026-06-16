from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import DataTable, Label

from cfmanager.core.logger import get_logger
from cfmanager.services.loadbalancers import LoadBalancerService
from cfmanager.services.zones import ZoneService
from cfmanager.tui.widgets.dialogs import ConfirmDialog
logger = get_logger()

# View modes
MODE_ZONES = "zones"
MODE_LBS = "lbs"
MODE_POOLS = "pools"


class LoadBalancerView(Widget):
    def __init__(self, **kwargs) -> None:
        self.selected_zone_id: Optional[str] = None
        self.selected_zone_name: Optional[str] = None
        self.mode: str = MODE_ZONES
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Container(id="main-content"):
            self.title_label = Label("⚖️ Load Balancers", id="screen-title")
            yield self.title_label
            self.hint_label = Label(
                "Press [bold]Enter[/bold] to select zone, "
                "[bold]p[/bold] for pools view, [bold]r[/bold] to refresh."
            )
            yield self.hint_label
            yield DataTable(id="lb-table")

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        self._setup_zones_columns(table)
        self.run_worker(self.refresh_data())

    # --- Column helpers ---

    def _setup_zones_columns(self, table: DataTable) -> None:
        table.clear(columns=True)
        table.add_columns("Zone ID", "Zone Name", "Status")

    def _setup_lbs_columns(self, table: DataTable) -> None:
        table.clear(columns=True)
        table.add_columns("LB ID", "Name", "Enabled", "Fallback Pool", "Created On")

    def _setup_pools_columns(self, table: DataTable) -> None:
        table.clear(columns=True)
        table.add_columns("Pool ID", "Name", "Enabled", "Description")

    # --- Data loading ---

    async def refresh_data(self) -> None:
        if self.mode == MODE_ZONES:
            await self._load_zones()
        elif self.mode == MODE_LBS:
            await self._load_lbs()
        elif self.mode == MODE_POOLS:
            await self._load_pools()

    async def _load_zones(self) -> None:
        table = self.query_one(DataTable)
        self._setup_zones_columns(table)
        self.title_label.update("⚖️ Load Balancers — Select a Zone")
        self.hint_label.update(
            "Press [bold]Enter[/bold] to view load balancers for a zone, "
            "[bold]p[/bold] for pools, [bold]r[/bold] to refresh."
        )

        zone_service = ZoneService(self.app.cf_client)
        try:
            zones = await zone_service.list_zones_async()
            for zone in zones:
                table.add_row(
                    zone["id"],
                    zone["name"],
                    zone.get("status", ""),
                    key=zone["id"],
                )
        except Exception as e:
            logger.exception("Failed to load zones for LB view in TUI")
            self.app.notify(f"Error loading zones: {e}", severity="error")

    async def _load_lbs(self) -> None:
        table = self.query_one(DataTable)
        self._setup_lbs_columns(table)
        self.title_label.update(f"⚖️ Load Balancers — {self.selected_zone_name}")
        self.hint_label.update(
            "Press [bold]d[/bold] to delete, [bold]p[/bold] for pools, "
            "[bold]b[/bold] to go back, [bold]r[/bold] to refresh."
        )

        lb_service = LoadBalancerService(self.app.cf_client)
        try:
            lbs = await lb_service.list_load_balancers_async(self.selected_zone_id)
            for lb in lbs:
                table.add_row(
                    lb.get("id", ""),
                    lb.get("name", ""),
                    "Yes" if lb.get("enabled") else "No",
                    lb.get("fallback_pool", ""),
                    str(lb.get("created_on", "")),
                    key=lb.get("id", ""),
                )
        except Exception as e:
            logger.exception("Failed to load load balancers in TUI")
            self.app.notify(f"Error loading load balancers: {e}", severity="error")

    async def _load_pools(self) -> None:
        table = self.query_one(DataTable)
        self._setup_pools_columns(table)
        self.title_label.update("⚖️ Load Balancer Pools")
        self.hint_label.update(
            "Press [bold]b[/bold] to go back, [bold]r[/bold] to refresh."
        )

        lb_service = LoadBalancerService(self.app.cf_client)
        try:
            pools = await lb_service.list_pools_async()
            for pool in pools:
                table.add_row(
                    pool.get("id", ""),
                    pool.get("name", ""),
                    "Yes" if pool.get("enabled") else "No",
                    pool.get("description", ""),
                    key=pool.get("id", ""),
                )
        except Exception as e:
            logger.exception("Failed to load LB pools in TUI")
            self.app.notify(f"Error loading pools: {e}", severity="error")

    # --- Navigation helpers ---

    def _go_to_zones(self) -> None:
        self.selected_zone_id = None
        self.selected_zone_name = None
        self.mode = MODE_ZONES
        self.run_worker(self.refresh_data())

    def _go_to_pools(self) -> None:
        self.mode = MODE_POOLS
        self.run_worker(self.refresh_data())

    # --- Key handling ---

    async def on_key(self, event) -> None:
        if event.key == "r":
            await self.refresh_data()
            return

        if event.key == "p":
            self._go_to_pools()
            return

        if event.key in ("b", "escape") and self.mode != MODE_ZONES:
            self._go_to_zones()
            return

        table = self.query_one(DataTable)
        if event.key == "d" and self.mode == MODE_LBS:
            if table.cursor_row is None or table.row_count == 0:
                return
            row_key = table.row_keys[table.cursor_row]
            lb_id = row_key.value
            row_values = table.get_row(row_key)
            lb_name = row_values[1]

            async def confirm_delete(confirm: bool) -> None:
                if confirm:
                    lb_service = LoadBalancerService(self.app.cf_client)
                    try:
                        await lb_service.delete_load_balancer_async(
                            self.selected_zone_id, lb_id
                        )
                        self.app.notify(
                            f"Deleted load balancer '{lb_name}'.", severity="success"
                        )
                        await self.refresh_data()
                    except Exception as e:
                        self.app.notify(f"Delete failed: {e}", severity="error")

            self.app.push_screen(
                ConfirmDialog(f"Delete load balancer '{lb_name}'?"),
                confirm_delete,
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if self.mode == MODE_ZONES:
            zone_id = event.row_key.value
            row_values = self.query_one(DataTable).get_row(event.row_key)
            zone_name = row_values[1]
            self.selected_zone_id = zone_id
            self.selected_zone_name = zone_name
            self.mode = MODE_LBS
            self.run_worker(self.refresh_data())

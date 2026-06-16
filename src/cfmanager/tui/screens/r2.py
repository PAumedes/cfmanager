from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, DataTable, Input, Label

from cfmanager.core.logger import get_logger
from cfmanager.services.r2 import R2Service
from cfmanager.tui.widgets.dialogs import ConfirmDialog
logger = get_logger()


class BucketFormDialog(ModalScreen[Optional[dict]]):
    def compose(self) -> ComposeResult:
        with Grid(classes="dialog-container"):
            with Vertical(classes="dialog-box"):
                yield Label("Create R2 Bucket", classes="dialog-title")
                yield Label("Bucket Name")
                yield Input(placeholder="my-bucket", id="bucket-name")
                yield Label("Location Hint (optional, e.g. WNAM, ENAM, WEUR, EEUR, APAC)")
                yield Input(placeholder="WNAM", id="bucket-location")
                with Horizontal():
                    yield Button("Create", variant="primary", id="bucket-save")
                    yield Button("Cancel", id="bucket-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "bucket-save":
            name = self.query_one("#bucket-name").value.strip()
            location = self.query_one("#bucket-location").value.strip()
            if not name:
                self.app.notify("Bucket name is required.", severity="error")
                return
            self.dismiss({"name": name, "location": location or None})
        else:
            self.dismiss(None)


class R2View(Widget):
    def compose(self) -> ComposeResult:
        with Container(id="main-content"):
            yield Label("📦 R2 Storage", id="screen-title")
            yield Label(
                "Press [bold]a[/bold] to create bucket, "
                "[bold]d[/bold] to delete, [bold]r[/bold] to refresh."
            )
            yield DataTable(id="r2-table")

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Bucket Name", "Creation Date", "Location")
        self.run_worker(self.refresh_data())

    async def refresh_data(self) -> None:
        table = self.query_one(DataTable)
        table.clear()

        r2_service = R2Service(self.app.cf_client)
        try:
            buckets = await r2_service.list_buckets_async()
            for bucket in buckets:
                table.add_row(
                    bucket.get("name", ""),
                    str(bucket.get("creation_date", "")),
                    bucket.get("location", ""),
                    key=bucket.get("name", ""),
                )
        except Exception as e:
            logger.exception("Failed to load R2 buckets in TUI")
            self.app.notify(f"Error loading R2 buckets: {e}", severity="error")

    async def on_key(self, event) -> None:
        table = self.query_one(DataTable)

        if event.key == "r":
            await self.refresh_data()
            return

        if event.key == "a":
            async def on_bucket_create(data: Optional[dict]) -> None:
                if data:
                    r2_service = R2Service(self.app.cf_client)
                    try:
                        await r2_service.create_bucket_async(
                            data["name"],
                            location_hint=data.get("location"),
                        )
                        self.app.notify(
                            f"Bucket '{data['name']}' created successfully.",
                            severity="success",
                        )
                        await self.refresh_data()
                    except Exception as e:
                        self.app.notify(f"Failed to create bucket: {e}", severity="error")

            self.app.push_screen(BucketFormDialog(), on_bucket_create)
            return

        if table.cursor_row is None or table.row_count == 0:
            return

        row_key = table.row_keys[table.cursor_row]
        bucket_name = row_key.value

        if event.key == "d":
            async def confirm_delete(confirm: bool) -> None:
                if confirm:
                    r2_service = R2Service(self.app.cf_client)
                    try:
                        await r2_service.delete_bucket_async(bucket_name)
                        self.app.notify(
                            f"Bucket '{bucket_name}' deleted.", severity="success"
                        )
                        await self.refresh_data()
                    except Exception as e:
                        self.app.notify(f"Delete failed: {e}", severity="error")

            self.app.push_screen(
                ConfirmDialog(f"Delete bucket '{bucket_name}'? This cannot be undone."),
                confirm_delete,
            )
